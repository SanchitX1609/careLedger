from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.models import Orphanage, Item, Inventory, UsageLog, Alert, db
from app.services import InventoryService, AlertService
from app.ai_forecasting import forecasting_engine

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Home page with dashboard"""
    # Get user's orphanage or first orphanage (for demo purposes)
    orphanage = current_user.orphanage if current_user.orphanage else Orphanage.query.first()
    
    if not orphanage:
        return render_template('setup.html')
    
    dashboard_data = InventoryService.get_dashboard_data(orphanage.id)
    return render_template('dashboard.html', data=dashboard_data)

@main_bp.route('/inventory')
@login_required
def inventory():
    """Inventory listing page"""
    # Use current user's orphanage or allow admin to view any orphanage
    if current_user.role.name == 'admin':
        orphanage_id = request.args.get('orphanage_id', 1, type=int)
    else:
        orphanage_id = current_user.orphanage_id if current_user.orphanage_id else 1
    
    category = request.args.get('category', '')
    
    # Get inventory items
    query = Inventory.query.filter_by(orphanage_id=orphanage_id)
    
    if category:
        query = query.join(Item).filter(Item.category == category)
    
    inventories = query.all()
    categories = Item.get_categories()
    
    return render_template('inventory.html', 
                         inventories=inventories, 
                         categories=categories,
                         selected_category=category)

@main_bp.route('/inventory/update', methods=['POST'])
@login_required
def update_inventory():
    """Update inventory stock levels"""
    data = request.get_json()
    
    result = InventoryService.update_stock(
        orphanage_id=data['orphanage_id'],
        item_id=data['item_id'],
        quantity_change=data['quantity_change'],
        operation=data.get('operation', 'add'),
        notes=data.get('notes')
    )
    
    return jsonify(result)

@main_bp.route('/usage')
@login_required
def usage():
    """Usage logging page"""
    # Use current user's orphanage or allow admin to view any orphanage
    if current_user.role.name == 'admin':
        orphanage_id = request.args.get('orphanage_id', 1, type=int)
    else:
        orphanage_id = current_user.orphanage_id if current_user.orphanage_id else 1
    
    # Get recent usage logs
    recent_usage = UsageLog.query.filter_by(orphanage_id=orphanage_id)\
                                 .order_by(UsageLog.date.desc())\
                                 .limit(50).all()
    
    # Get items for dropdown
    items = Item.query.all()
    
    return render_template('usage.html', 
                         recent_usage=recent_usage,
                         items=items,
                         orphanage_id=orphanage_id)

@main_bp.route('/usage/log', methods=['POST'])
@login_required
def log_usage():
    """Log daily usage"""
    data = request.get_json()
    
    result = InventoryService.log_daily_usage(
        orphanage_id=data['orphanage_id'],
        item_id=data['item_id'],
        quantity_used=data['quantity_used'],
        notes=data.get('notes'),
        usage_date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None
    )
    
    return jsonify(result)

@main_bp.route('/forecasting')
@login_required
def forecasting():
    """AI Forecasting page"""
    # Use current user's orphanage or allow admin to view any orphanage
    if current_user.role.name == 'admin':
        orphanage_id = request.args.get('orphanage_id', 1, type=int)
    else:
        orphanage_id = current_user.orphanage_id if current_user.orphanage_id else 1
    
    item_id = request.args.get('item_id', type=int)
    
    if not item_id:
        # Show item selection
        items = db.session.query(Item)\
                         .join(Inventory)\
                         .filter(Inventory.orphanage_id == orphanage_id)\
                         .all()
        return render_template('forecasting_select.html', items=items, orphanage_id=orphanage_id)
    
    # Get forecasting data
    forecasting_data = InventoryService.get_forecasting_data(orphanage_id, item_id)
    item = Item.query.get(item_id)
    inventory = Inventory.query.filter_by(orphanage_id=orphanage_id, item_id=item_id).first()
    
    # Create serializable versions for JavaScript
    item_data = {
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'category': item.category,
        'unit': item.unit
    } if item else None
    
    inventory_data = {
        'id': inventory.id,
        'quantity': inventory.quantity,
        'minimum_level': inventory.minimum_level,
        'maximum_level': inventory.maximum_level,
        'last_updated': inventory.last_updated.isoformat() if inventory.last_updated else None
    } if inventory else None
    
    return render_template('forecasting.html', 
                         forecasting_data=forecasting_data,
                         item=item,
                         inventory=inventory,
                         item_data=item_data,
                         inventory_data=inventory_data)

@main_bp.route('/api/forecasting/<int:orphanage_id>/<int:item_id>')
@login_required
def api_forecasting(orphanage_id, item_id):
    """API endpoint for forecasting data"""
    forecasting_data = InventoryService.get_forecasting_data(orphanage_id, item_id)
    return jsonify(forecasting_data)

@main_bp.route('/chart-test')
def chart_test():
    """Test page for charts"""
    return render_template('chart_test.html')


@main_bp.route('/alerts')
@login_required
def alerts():
    """Alerts page"""
    # Use current user's orphanage or allow admin to view any orphanage
    if current_user.role.name == 'admin':
        orphanage_id = request.args.get('orphanage_id', 1, type=int)
    else:
        orphanage_id = current_user.orphanage_id if current_user.orphanage_id else 1
    
    alerts = Alert.query.filter_by(orphanage_id=orphanage_id)\
                       .order_by(Alert.created_at.desc()).all()
    
    alerts_summary = AlertService.get_alerts_summary(orphanage_id)
    
    return render_template('alerts.html', alerts=alerts, alerts_summary=alerts_summary)

@main_bp.route('/alerts/mark_read/<int:alert_id>', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """Mark alert as read"""
    success = AlertService.mark_alert_as_read(alert_id)
    return jsonify({'success': success})

@main_bp.route('/reports')
@login_required
def reports():
    """Reports page"""
    # Use current user's orphanage or allow admin to view any orphanage
    if current_user.role.name == 'admin':
        orphanage_id = request.args.get('orphanage_id', 1, type=int)
    else:
        orphanage_id = current_user.orphanage_id if current_user.orphanage_id else 1
    
    # Default to last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get date range from query params
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    
    # Get usage report and summary statistics
    usage_report = InventoryService.generate_usage_report(orphanage_id, start_date, end_date)
    summary_stats = InventoryService.get_report_summary_stats(orphanage_id)
    
    return render_template('reports.html', 
                         usage_report=usage_report,
                         start_date=start_date,
                         end_date=end_date,
                         total_items=summary_stats['total_items'],
                         low_stock_count=summary_stats['low_stock_count'],
                         total_usage_logs=summary_stats['total_usage_logs'],
                         total_orphanages=summary_stats['total_orphanages'])

@main_bp.route('/items')
@login_required
def items():
    """Items management page"""
    items = Item.query.all()
    categories = Item.get_categories()
    
    return render_template('items.html', items=items, categories=categories)

@main_bp.route('/items/add', methods=['POST'])
@login_required
def add_item():
    """Add new item"""
    data = request.get_json()
    
    try:
        item = Item(
            name=data['name'],
            category=data['category'],
            unit=data['unit'],
            description=data.get('description', ''),
            expiry_applicable=data.get('expiry_applicable', False)
        )
        db.session.add(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error adding item: {str(e)}'})

@main_bp.route('/orphanages')
@login_required
def orphanages():
    """Orphanages management page"""
    # Only admins can manage all orphanages
    if current_user.role.name != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    orphanages = Orphanage.query.all()
    return render_template('orphanages.html', orphanages=orphanages)

@main_bp.route('/api/dashboard/<int:orphanage_id>')
@login_required
def api_dashboard(orphanage_id):
    """API endpoint for dashboard data"""
    dashboard_data = InventoryService.get_dashboard_data(orphanage_id)
    
    # Convert data to JSON-serializable format
    if dashboard_data:
        # Remove non-serializable objects
        api_data = {
            'summary': dashboard_data['summary'],
            'category_stats': dashboard_data['category_stats'],
            'low_stock_items': [
                {
                    'item_name': inv.item.name,
                    'current_stock': inv.quantity,
                    'minimum_level': inv.minimum_level,
                    'unit': inv.item.unit,
                    'category': inv.item.category
                } for inv in dashboard_data['low_stock_items']
            ],
            'recent_usage': [
                {
                    'item_name': log.item.name,
                    'quantity_used': log.quantity_used,
                    'date': log.date.isoformat(),
                    'unit': log.item.unit
                } for log in dashboard_data['recent_usage']
            ]
        }
        return jsonify(api_data)
    
    return jsonify({'error': 'Orphanage not found'}), 404

@main_bp.route('/check_alerts')
@login_required
def check_alerts():
    """Manual alert check endpoint"""
    alerts_created = InventoryService.check_and_create_alerts()
    return jsonify({'alerts_created': alerts_created})

# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@main_bp.route('/items/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify({
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'unit': item.unit,
        'description': item.description,
        'expiry_applicable': item.expiry_applicable
    })

@main_bp.route('/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    data = request.get_json()
    item = Item.query.get_or_404(item_id)
    item.name = data.get('name', item.name)
    item.category = data.get('category', item.category)
    item.unit = data.get('unit', item.unit)
    item.description = data.get('description', item.description)
    item.expiry_applicable = data.get('expiry_applicable', item.expiry_applicable)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item updated'})

@main_bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item deleted'})

@main_bp.route('/orphanages/<int:orphanage_id>', methods=['GET'])
@login_required
def get_orphanage(orphanage_id):
    orphanage = Orphanage.query.get_or_404(orphanage_id)
    return jsonify({
        'success': True,
        'orphanage': {
            'id': orphanage.id,
            'name': orphanage.name,
            'location': orphanage.location,
            'contact_person': orphanage.contact_person,
            'phone': orphanage.contact_phone,
            'email': orphanage.contact_email,
            'description': getattr(orphanage, 'description', '')  # Handle missing field gracefully
        }
    })

@main_bp.route('/orphanages', methods=['POST'])
@login_required
def add_orphanage():
    # Only admins can add orphanages
    if current_user.role.name != 'admin':
        return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
    
    data = request.get_json()
    try:
        orphanage = Orphanage(
            name=data['name'],
            location=data['location'],
            contact_person=data.get('contact_person'),
            contact_phone=data.get('phone'),
            contact_email=data.get('email')
        )
        db.session.add(orphanage)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Orphanage added successfully', 'id': orphanage.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error adding orphanage: {str(e)}'})

@main_bp.route('/orphanages/<int:orphanage_id>', methods=['PUT'])
@login_required
def update_orphanage(orphanage_id):
    # Only admins can update orphanages
    if current_user.role.name != 'admin':
        return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
    
    data = request.get_json()
    try:
        orphanage = Orphanage.query.get_or_404(orphanage_id)
        orphanage.name = data.get('name', orphanage.name)
        orphanage.location = data.get('location', orphanage.location)
        orphanage.contact_person = data.get('contact_person', orphanage.contact_person)
        # Map frontend field names to backend field names
        orphanage.contact_phone = data.get('phone', orphanage.contact_phone)
        orphanage.contact_email = data.get('email', orphanage.contact_email)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Orphanage updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating orphanage: {str(e)}'})

@main_bp.route('/orphanages/<int:orphanage_id>', methods=['DELETE'])
@login_required
def delete_orphanage(orphanage_id):
    # Only admins can delete orphanages
    if current_user.role.name != 'admin':
        return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
    
    try:
        orphanage = Orphanage.query.get_or_404(orphanage_id)
        
        # Check if orphanage has any related data that would prevent deletion
        if orphanage.inventories:
            return jsonify({'success': False, 'message': 'Cannot delete orphanage with existing inventory records. Please remove all inventory items first.'})
        
        db.session.delete(orphanage)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Orphanage deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting orphanage: {str(e)}'})

@main_bp.route('/inventory/<int:inventory_id>', methods=['GET'])
@login_required
def get_inventory(inventory_id):
    inv = Inventory.query.get_or_404(inventory_id)
    return jsonify({
        'id': inv.id,
        'orphanage_id': inv.orphanage_id,
        'item_id': inv.item_id,
        'quantity': inv.quantity,
        'minimum_level': inv.minimum_level,
        'maximum_level': inv.maximum_level,
        'expiry_date': inv.expiry_date.isoformat() if inv.expiry_date else None,
        'last_updated': inv.last_updated.isoformat() if inv.last_updated else None
    })

@main_bp.route('/inventory', methods=['POST'])
@login_required
def add_inventory():
    data = request.get_json()
    inv = Inventory(
        orphanage_id=data['orphanage_id'],
        item_id=data['item_id'],
        quantity=data['quantity'],
        minimum_level=data['minimum_level'],
        maximum_level=data.get('maximum_level'),
        expiry_date=data.get('expiry_date')
    )
    db.session.add(inv)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inventory item added', 'id': inv.id})

@main_bp.route('/inventory/<int:inventory_id>', methods=['PUT'])
@login_required
def update_inventory_item(inventory_id):
    data = request.get_json()
    inv = Inventory.query.get_or_404(inventory_id)
    inv.quantity = data.get('quantity', inv.quantity)
    inv.minimum_level = data.get('minimum_level', inv.minimum_level)
    inv.maximum_level = data.get('maximum_level', inv.maximum_level)
    if data.get('expiry_date'):
        inv.expiry_date = data['expiry_date']
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inventory updated'})

@main_bp.route('/inventory/<int:inventory_id>', methods=['DELETE'])
@login_required
def delete_inventory(inventory_id):
    inv = Inventory.query.get_or_404(inventory_id)
    db.session.delete(inv)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inventory deleted'})

@main_bp.route('/usage_logs/<int:log_id>', methods=['GET'])
@login_required
def get_usage_log(log_id):
    log = UsageLog.query.get_or_404(log_id)
    return jsonify({
        'id': log.id,
        'orphanage_id': log.orphanage_id,
        'item_id': log.item_id,
        'date': log.date.isoformat(),
        'quantity_used': log.quantity_used,
        'notes': log.notes,
        'recorded_by': log.recorded_by,
        'created_at': log.created_at.isoformat() if log.created_at else None
    })

@main_bp.route('/usage_logs', methods=['POST'])
@login_required
def add_usage_log():
    data = request.get_json()
    log = UsageLog(
        orphanage_id=data['orphanage_id'],
        item_id=data['item_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else date.today(),
        quantity_used=data['quantity_used'],
        notes=data.get('notes'),
        recorded_by=data.get('recorded_by')
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usage log added', 'id': log.id})

@main_bp.route('/usage_logs/<int:log_id>', methods=['PUT'])
@login_required
def update_usage_log(log_id):
    data = request.get_json()
    log = UsageLog.query.get_or_404(log_id)
    log.quantity_used = data.get('quantity_used', log.quantity_used)
    log.notes = data.get('notes', log.notes)
    log.date = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else log.date
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usage log updated'})

@main_bp.route('/usage_logs/<int:log_id>', methods=['DELETE'])
@login_required
def delete_usage_log(log_id):
    log = UsageLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usage log deleted'})

@main_bp.route('/alerts/<int:alert_id>', methods=['GET'])
@login_required
def get_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    return jsonify({
        'id': alert.id,
        'orphanage_id': alert.orphanage_id,
        'item_id': alert.item_id,
        'alert_type': alert.alert_type,
        'title': alert.title,
        'message': alert.message,
        'is_read': alert.is_read,
        'created_at': alert.created_at.isoformat() if alert.created_at else None
    })

@main_bp.route('/alerts/<int:alert_id>', methods=['PUT'])
@login_required
def update_alert(alert_id):
    data = request.get_json()
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = data.get('is_read', alert.is_read)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Alert updated'})

@main_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
@login_required
def delete_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    db.session.delete(alert)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Alert deleted'})
