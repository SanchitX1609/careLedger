from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from app import db

class Role(db.Model):
    """Model for user roles"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    """Model for user authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Foreign Keys
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    orphanage_id = db.Column(db.Integer, db.ForeignKey('orphanages.id'))
    
    # Relationships
    orphanage = db.relationship('Orphanage', backref='users')
    usage_logs = db.relationship('UsageLog', backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.role and self.role.name == role_name
    
    def can_access_orphanage(self, orphanage_id):
        """Check if user can access specific orphanage data"""
        if self.has_role('admin'):
            return True
        return self.orphanage_id == orphanage_id
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'

class Orphanage(db.Model):
    """Model for orphanage/care facility information"""
    __tablename__ = 'orphanages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventories = db.relationship('Inventory', backref='orphanage', lazy=True, cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', backref='orphanage', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Orphanage {self.name}>'
    
    def get_low_stock_items(self):
        """Get items that are below minimum threshold"""
        return [inv for inv in self.inventories if inv.is_low_stock()]
    
    def get_critical_stock_items(self):
        """Get items that are critically low (below 50% of minimum)"""
        return [inv for inv in self.inventories if inv.is_critical_stock()]

class Item(db.Model):
    """Model for inventory items"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, tablets, pieces, etc.
    description = db.Column(db.Text)
    expiry_applicable = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventories = db.relationship('Inventory', backref='item', lazy=True, cascade='all, delete-orphan')
    usage_logs = db.relationship('UsageLog', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    @staticmethod
    def get_categories():
        """Get all unique categories"""
        return [cat[0] for cat in db.session.query(Item.category.distinct()).all()]

class Inventory(db.Model):
    """Model for current inventory levels"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    orphanage_id = db.Column(db.Integer, db.ForeignKey('orphanages.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    minimum_level = db.Column(db.Float, nullable=False)
    maximum_level = db.Column(db.Float)
    expiry_date = db.Column(db.Date)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate entries
    __table_args__ = (db.UniqueConstraint('orphanage_id', 'item_id'),)
    
    def __repr__(self):
        return f'<Inventory {self.item.name}: {self.quantity} {self.item.unit}>'
    
    def is_low_stock(self):
        """Check if item is below minimum level"""
        return self.quantity <= self.minimum_level
    
    def is_critical_stock(self):
        """Check if item is critically low (below 50% of minimum)"""
        return self.quantity <= (self.minimum_level * 0.5)
    
    def stock_level_percentage(self):
        """Get stock level as percentage of minimum level"""
        if self.minimum_level == 0:
            return 100
        return (self.quantity / self.minimum_level) * 100
    
    def days_until_expiry(self):
        """Get days until expiry"""
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None
    
    def is_expired(self):
        """Check if item is expired"""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False
    
    def is_expiring_soon(self, days=7):
        """Check if item is expiring within specified days"""
        if self.expiry_date:
            return 0 < (self.expiry_date - date.today()).days <= days
        return False

class UsageLog(db.Model):
    """Model for daily usage tracking"""
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    orphanage_id = db.Column(db.Integer, db.ForeignKey('orphanages.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Added ForeignKey to users table
    date = db.Column(db.Date, nullable=False, default=date.today)
    quantity_used = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    recorded_by = db.Column(db.String(100)) # This might be redundant or used if user_id is null
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UsageLog {self.item.name}: {self.quantity_used} on {self.date}>'
    
    @staticmethod
    def get_usage_for_period(orphanage_id, item_id, start_date, end_date):
        """Get usage data for a specific period"""
        return UsageLog.query.filter(
            UsageLog.orphanage_id == orphanage_id,
            UsageLog.item_id == item_id,
            UsageLog.date >= start_date,
            UsageLog.date <= end_date
        ).all()

class Alert(db.Model):
    """Model for system alerts"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    orphanage_id = db.Column(db.Integer, db.ForeignKey('orphanages.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    alert_type = db.Column(db.String(50), nullable=False)  # low_stock, critical_stock, expiring, expired
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orphanage = db.relationship('Orphanage', backref='alerts')
    item = db.relationship('Item', backref='alerts')
    
    def __repr__(self):
        return f'<Alert {self.title}>'
    
    @staticmethod
    def create_low_stock_alert(inventory):
        """Create a low stock alert for an inventory item"""
        alert = Alert(
            orphanage_id=inventory.orphanage_id,
            item_id=inventory.item_id,
            alert_type='low_stock',
            title=f'Low Stock: {inventory.item.name}',
            message=f'{inventory.item.name} is running low. Current stock: {inventory.quantity} {inventory.item.unit}, Minimum level: {inventory.minimum_level} {inventory.item.unit}'
        )
        return alert
    
    @staticmethod
    def create_expiry_alert(inventory):
        """Create an expiry alert for an inventory item"""
        days_left = inventory.days_until_expiry()
        alert = Alert(
            orphanage_id=inventory.orphanage_id,
            item_id=inventory.item_id,
            alert_type='expiring' if days_left > 0 else 'expired',
            title=f'Expiry Alert: {inventory.item.name}',
            message=f'{inventory.item.name} {"expires in " + str(days_left) + " days" if days_left > 0 else "has expired"}'
        )
        return alert
