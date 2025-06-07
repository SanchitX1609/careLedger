from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    cache.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import main_bp
    from app.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    # Create database tables and initialize data
    with app.app_context():
        db.create_all()
        
        # Initialize sample data if database is empty
        from app.models import Orphanage, Item, Role
        if Role.query.count() == 0:
            init_roles()
        if Orphanage.query.count() == 0:
            init_sample_data()
    
    return app

def init_roles():
    """Initialize default roles"""
    from app.models import Role
    
    roles = [
        {'name': 'admin', 'description': 'Full system access'},
        {'name': 'manager', 'description': 'Manage orphanage operations'},
        {'name': 'staff', 'description': 'Basic inventory operations'},
        {'name': 'viewer', 'description': 'Read-only access'}
    ]
    
    for role_data in roles:
        role = Role(name=role_data['name'], description=role_data['description'])
        db.session.add(role)
    
    db.session.commit()
    print("Default roles created successfully!")

def init_sample_data():
    """Initialize the database with sample data for demonstration"""
    from app.models import Orphanage, Item, Inventory
    from datetime import datetime
    
    # Create sample orphanage
    orphanage = Orphanage(
        name="Hope Children's Home",
        location="Mumbai, Maharashtra",
        contact_person="SJ",
        contact_phone="+91-9876543210",
        contact_email="contact@hopechildrenshome.org"
    )
    db.session.add(orphanage)
    db.session.flush()  # Get the ID
    
    # Create sample items
    sample_items = [
        {"name": "Rice", "category": "Food", "unit": "kg", "current_stock": 50, "min_level": 20},
        {"name": "Dal (Lentils)", "category": "Food", "unit": "kg", "current_stock": 25, "min_level": 10},
        {"name": "Cooking Oil", "category": "Food", "unit": "liters", "current_stock": 8, "min_level": 5},
        {"name": "Paracetamol", "category": "Medicine", "unit": "tablets", "current_stock": 100, "min_level": 50},
        {"name": "Bandages", "category": "Medicine", "unit": "rolls", "current_stock": 15, "min_level": 10},
        {"name": "Children's Shirts", "category": "Clothing", "unit": "pieces", "current_stock": 30, "min_level": 15},
        {"name": "Soap", "category": "Hygiene", "unit": "bars", "current_stock": 20, "min_level": 12},
        {"name": "Toothpaste", "category": "Hygiene", "unit": "tubes", "current_stock": 8, "min_level": 6},
    ]
    
    for item_data in sample_items:
        item = Item(
            name=item_data["name"],
            category=item_data["category"],
            unit=item_data["unit"]
        )
        db.session.add(item)
        db.session.flush()
        
        # Create inventory entry
        inventory = Inventory(
            orphanage_id=orphanage.id,
            item_id=item.id,
            quantity=item_data["current_stock"],
            minimum_level=item_data["min_level"]
        )
        db.session.add(inventory)
    
    db.session.commit()
    print("Sample data initialized successfully!")
