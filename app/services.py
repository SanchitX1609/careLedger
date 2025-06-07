from datetime import datetime, date, timedelta
from app.models import Inventory, UsageLog, Alert, Orphanage, Item
from app.ai_forecasting import forecasting_engine
from app import db

class InventoryService:
    """Service class for inventory management operations"""
    
    @staticmethod
    def update_stock(orphanage_id, item_id, quantity_change, operation='add', notes=None):
        """Update inventory stock levels"""
        inventory = Inventory.query.filter_by(
            orphanage_id=orphanage_id,
            item_id=item_id
        ).first()
        
        if not inventory:
            return {"success": False, "message": "Inventory item not found"}
        
        old_quantity = inventory.quantity
        
        if operation == 'add':
            inventory.quantity += quantity_change
        elif operation == 'subtract':
            inventory.quantity = max(0, inventory.quantity - quantity_change)
        elif operation == 'set':
            inventory.quantity = quantity_change
        
        inventory.last_updated = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # Create usage log if subtracting (consumption)
            if operation == 'subtract' and quantity_change > 0:
                usage_log = UsageLog(
                    orphanage_id=orphanage_id,
                    item_id=item_id,
                    quantity_used=quantity_change,
                    notes=notes,
                    date=date.today()
                )
                db.session.add(usage_log)
                db.session.commit()
            
            # Check for alerts
            InventoryService.check_and_create_alerts(inventory)
            
            return {
                "success": True,
                "message": f"Stock updated from {old_quantity} to {inventory.quantity}",
                "new_quantity": inventory.quantity
            }
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Error updating stock: {str(e)}"}
    
    @staticmethod
    def log_daily_usage(orphanage_id, item_id, quantity_used, notes=None, usage_date=None):
        """Log daily usage and update inventory"""
        if usage_date is None:
            usage_date = date.today()
        
        # Check if usage already logged for this date
        existing_log = UsageLog.query.filter_by(
            orphanage_id=orphanage_id,
            item_id=item_id,
            date=usage_date
        ).first()
        
        if existing_log:
            # Update existing log
            old_quantity = existing_log.quantity_used
            existing_log.quantity_used = quantity_used
            existing_log.notes = notes
            existing_log.created_at = datetime.utcnow()
            
            # Adjust inventory (add back old quantity, subtract new quantity)
            quantity_adjustment = old_quantity - quantity_used
        else:
            # Create new log
            usage_log = UsageLog(
                orphanage_id=orphanage_id,
                item_id=item_id,
                quantity_used=quantity_used,
                notes=notes,
                date=usage_date
            )
            db.session.add(usage_log)
            quantity_adjustment = -quantity_used
        
        # Update inventory
        result = InventoryService.update_stock(
            orphanage_id, item_id, abs(quantity_adjustment),
            operation='add' if quantity_adjustment > 0 else 'subtract'
        )
        
        if result["success"]:
            try:
                db.session.commit()
                return {"success": True, "message": "Usage logged successfully"}
            except Exception as e:
                db.session.rollback()
                return {"success": False, "message": f"Error logging usage: {str(e)}"}
        else:
            return result
    
    @staticmethod
    def check_and_create_alerts(inventory=None):
        """Check inventory levels and create alerts as needed"""
        if inventory:
            inventories = [inventory]
        else:
            inventories = Inventory.query.all()
        
        alerts_created = 0
        
        for inv in inventories:
            # Check for existing alerts to avoid duplicates
            existing_alert = Alert.query.filter_by(
                orphanage_id=inv.orphanage_id,
                item_id=inv.item_id,
                is_read=False
            ).first()
            
            alert_created = False
            
            # Low stock alert
            if inv.is_critical_stock() and not existing_alert:
                alert = Alert.create_low_stock_alert(inv)
                alert.alert_type = 'critical_stock'
                alert.title = f'Critical Stock Alert: {inv.item.name}'
                db.session.add(alert)
                alert_created = True
            elif inv.is_low_stock() and not existing_alert:
                alert = Alert.create_low_stock_alert(inv)
                db.session.add(alert)
                alert_created = True
            
            # Expiry alerts
            if inv.expiry_date:
                if inv.is_expired() and not existing_alert:
                    alert = Alert.create_expiry_alert(inv)
                    db.session.add(alert)
                    alert_created = True
                elif inv.is_expiring_soon() and not existing_alert:
                    alert = Alert.create_expiry_alert(inv)
                    db.session.add(alert)
                    alert_created = True
            
            if alert_created:
                alerts_created += 1
        
        if alerts_created > 0:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        
        return alerts_created
    
    @staticmethod
    def get_dashboard_data(orphanage_id):
        """Get comprehensive dashboard data for an orphanage"""
        orphanage = Orphanage.query.get(orphanage_id)
        if not orphanage:
            return None
        
        # Get inventory summary
        inventories = Inventory.query.filter_by(orphanage_id=orphanage_id).all()
        
        total_items = len(inventories)
        low_stock_items = [inv for inv in inventories if inv.is_low_stock()]
        critical_stock_items = [inv for inv in inventories if inv.is_critical_stock()]
        expiring_items = [inv for inv in inventories if inv.is_expiring_soon()]
        
        # Get recent usage
        recent_usage = UsageLog.query.filter_by(orphanage_id=orphanage_id)\
                                    .filter(UsageLog.date >= date.today() - timedelta(days=7))\
                                    .order_by(UsageLog.date.desc())\
                                    .limit(10).all()
        
        # Get active alerts
        active_alerts = Alert.query.filter_by(orphanage_id=orphanage_id, is_read=False)\
                                  .order_by(Alert.created_at.desc()).all()
        
        # Category breakdown
        category_stats = {}
        for inv in inventories:
            category = inv.item.category
            if category not in category_stats:
                category_stats[category] = {
                    'total_items': 0,
                    'low_stock': 0,
                    'total_value': 0  # Could be enhanced with item prices
                }
            category_stats[category]['total_items'] += 1
            if inv.is_low_stock():
                category_stats[category]['low_stock'] += 1
        
        return {
            'orphanage': orphanage,
            'summary': {
                'total_items': total_items,
                'low_stock_count': len(low_stock_items),
                'critical_stock_count': len(critical_stock_items),
                'expiring_items_count': len(expiring_items),
                'active_alerts_count': len(active_alerts)
            },
            'low_stock_items': low_stock_items,
            'critical_stock_items': critical_stock_items,
            'expiring_items': expiring_items,
            'recent_usage': recent_usage,
            'active_alerts': active_alerts,
            'category_stats': category_stats
        }
    
    @staticmethod
    def get_forecasting_data(orphanage_id, item_id):
        """Get AI forecasting data for an item"""
        try:
            usage_prediction = forecasting_engine.predict_usage(orphanage_id, item_id)
            stockout_prediction = forecasting_engine.predict_stockout(orphanage_id, item_id)
            reorder_recommendation = forecasting_engine.get_reorder_recommendation(orphanage_id, item_id)
            
            return {
                'usage_prediction': usage_prediction,
                'stockout_prediction': stockout_prediction,
                'reorder_recommendation': reorder_recommendation
            }
        except Exception as e:
            return {
                'error': f"Forecasting error: {str(e)}",
                'usage_prediction': None,
                'stockout_prediction': None,
                'reorder_recommendation': None
            }
    
    @staticmethod
    def generate_usage_report(orphanage_id, start_date, end_date):
        """Generate usage report for a date range"""
        usage_logs = UsageLog.query.filter(
            UsageLog.orphanage_id == orphanage_id,
            UsageLog.date >= start_date,
            UsageLog.date <= end_date
        ).order_by(UsageLog.date.desc()).all()
        
        # Group by item
        item_usage = {}
        for log in usage_logs:
            item_name = log.item.name
            if item_name not in item_usage:
                item_usage[item_name] = {
                    'total_used': 0,
                    'unit': log.item.unit,
                    'category': log.item.category,
                    'daily_usage': []
                }
            item_usage[item_name]['total_used'] += log.quantity_used
            item_usage[item_name]['daily_usage'].append({
                'date': log.date,
                'quantity': log.quantity_used,
                'notes': log.notes
            })
        
        return {
            'period': f"{start_date} to {end_date}",
            'total_logs': len(usage_logs),
            'item_usage': item_usage
        }

class AlertService:
    """Service class for alert management"""
    
    @staticmethod
    def mark_alert_as_read(alert_id):
        """Mark an alert as read"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_alerts_summary(orphanage_id):
        """Get alerts summary for an orphanage"""
        alerts = Alert.query.filter_by(orphanage_id=orphanage_id).all()
        
        summary = {
            'total': len(alerts),
            'unread': len([a for a in alerts if not a.is_read]),
            'by_type': {}
        }
        
        for alert in alerts:
            alert_type = alert.alert_type
            if alert_type not in summary['by_type']:
                summary['by_type'][alert_type] = {'total': 0, 'unread': 0}
            
            summary['by_type'][alert_type]['total'] += 1
            if not alert.is_read:
                summary['by_type'][alert_type]['unread'] += 1
        
        return summary
