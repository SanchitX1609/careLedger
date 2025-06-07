import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error
from datetime import datetime, date, timedelta
from app.models import UsageLog, Inventory
from app import db

class ForecastingEngine:
    """AI-powered forecasting engine for inventory management"""
    
    def __init__(self):
        self.min_data_points = 5
        self.default_forecast_days = 7
    
    def get_usage_data(self, orphanage_id, item_id, days_back=30):
        """Get historical usage data for an item"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        usage_logs = UsageLog.get_usage_for_period(
            orphanage_id, item_id, start_date, end_date
        )
        
        if not usage_logs:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for log in usage_logs:
            data.append({
                'date': log.date,
                'quantity_used': log.quantity_used,
                'day_of_week': log.date.weekday(),
                'day_number': (log.date - start_date).days
            })
        
        df = pd.DataFrame(data)
        
        # Fill missing dates with 0 usage
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        df_complete = pd.DataFrame({'date': date_range})
        df_complete['date'] = df_complete['date'].dt.date
        
        df = df_complete.merge(df, on='date', how='left')
        df['quantity_used'] = df['quantity_used'].fillna(0)
        df['day_of_week'] = df['date'].apply(lambda x: x.weekday())
        df['day_number'] = df['date'].apply(lambda x: (x - start_date).days)
        
        return df
    
    def predict_usage(self, orphanage_id, item_id, forecast_days=None):
        """Predict future usage for an item"""
        if forecast_days is None:
            forecast_days = self.default_forecast_days
        
        df = self.get_usage_data(orphanage_id, item_id)
        
        if len(df) < self.min_data_points:
            # Not enough data, use average of available data or default
            if len(df) > 0:
                avg_usage = df['quantity_used'].mean()
            else:
                avg_usage = 0
            
            return {
                'predictions': [avg_usage] * forecast_days,
                'total_predicted': avg_usage * forecast_days,
                'confidence': 'low',
                'method': 'average',
                'accuracy': None
            }
        
        # Prepare features
        X = df[['day_number', 'day_of_week']].values
        y = df['quantity_used'].values
        
        # Try different models and pick the best one
        models = self._get_models()
        best_model = None
        best_score = float('inf')
        best_method = 'linear'
        
        for model_name, model in models.items():
            try:
                model.fit(X, y)
                predictions = model.predict(X)
                score = mean_absolute_error(y, predictions)
                
                if score < best_score:
                    best_score = score
                    best_model = model
                    best_method = model_name
            except Exception as e:
                continue
        
        if best_model is None:
            # Fallback to simple average
            avg_usage = df['quantity_used'].mean()
            return {
                'predictions': [avg_usage] * forecast_days,
                'total_predicted': avg_usage * forecast_days,
                'confidence': 'low',
                'method': 'average',
                'accuracy': None
            }
        
        # Generate future predictions
        last_day = df['day_number'].max()
        future_predictions = []
        
        for i in range(1, forecast_days + 1):
            future_day = last_day + i
            future_date = date.today() + timedelta(days=i)
            future_dow = future_date.weekday()
            
            prediction = best_model.predict([[future_day, future_dow]])[0]
            future_predictions.append(max(0, prediction))  # Ensure non-negative
        
        # Calculate confidence based on model accuracy
        confidence = self._calculate_confidence(best_score, df['quantity_used'].std())
        
        return {
            'predictions': future_predictions,
            'total_predicted': sum(future_predictions),
            'confidence': confidence,
            'method': best_method,
            'accuracy': best_score
        }
    
    def predict_stockout(self, orphanage_id, item_id, forecast_days=None):
        """Predict when an item will run out of stock"""
        if forecast_days is None:
            forecast_days = self.default_forecast_days
        
        # Get current inventory
        inventory = Inventory.query.filter_by(
            orphanage_id=orphanage_id,
            item_id=item_id
        ).first()
        
        if not inventory:
            return None
        
        # Get usage prediction
        forecast = self.predict_usage(orphanage_id, item_id, forecast_days)
        
        current_stock = inventory.quantity if inventory.quantity is not None else 0
        daily_predictions = forecast['predictions']
        
        # Calculate day-by-day stock levels
        stock_levels = []
        running_stock = current_stock
        
        for day, predicted_usage in enumerate(daily_predictions, 1):
            running_stock -= predicted_usage
            stock_levels.append({
                'day': day,
                'date': date.today() + timedelta(days=day),
                'predicted_usage': predicted_usage,
                'remaining_stock': max(0, running_stock),
                'stockout': running_stock <= 0
            })
        
        # Find stockout day
        stockout_day = None
        for level in stock_levels:
            if level['stockout']:
                stockout_day = level['day']
                break
        
        return {
            'current_stock': current_stock,
            'stockout_day': stockout_day,
            'stockout_date': date.today() + timedelta(days=stockout_day) if stockout_day else None,
            'stock_levels': stock_levels,
            'forecast_confidence': forecast['confidence'],
            'total_predicted_usage': forecast['total_predicted']
        }
    
    def get_reorder_recommendation(self, orphanage_id, item_id):
        """Get reorder recommendations for an item"""
        inventory = Inventory.query.filter_by(
            orphanage_id=orphanage_id,
            item_id=item_id
        ).first()
        
        if not inventory:
            return None
        
        # Get 30-day usage forecast
        forecast = self.predict_usage(orphanage_id, item_id, 30)
        stockout_prediction = self.predict_stockout(orphanage_id, item_id, 30) # This can be None
        
        # Calculate recommended order quantity
        monthly_usage = forecast['total_predicted']
        current_stock = inventory.quantity if inventory.quantity is not None else 0
        minimum_level = inventory.minimum_level if inventory.minimum_level is not None else 0
        
        # Safety stock (1.5x minimum level)
        safety_stock = minimum_level * 1.5
        
        reorder_quantity = 0
        urgency = 'low' # Default urgency

        # Recommended order quantity
        if stockout_prediction and stockout_prediction.get('stockout_day') is not None:
            # Urgent reorder needed
            days_to_stockout = stockout_prediction['stockout_day']
            reorder_quantity = monthly_usage + safety_stock - current_stock
            urgency = 'urgent' if days_to_stockout <= 3 else 'high'
        else:
            # Regular reorder or stockout_prediction is None or stockout_day is None
            reorder_quantity = max(0, (monthly_usage + safety_stock) - current_stock)
            urgency = 'medium' if current_stock <= minimum_level else 'low' # This comparison is now safe
        
        return {
            'item_name': inventory.item.name,
            'current_stock': current_stock,
            'minimum_level': minimum_level,
            'predicted_monthly_usage': monthly_usage,
            'recommended_quantity': max(0, reorder_quantity),
            'urgency': urgency,
            'stockout_risk': stockout_prediction.get('stockout_day') is not None if stockout_prediction else False,
            'stockout_date': stockout_prediction.get('stockout_date') if stockout_prediction else None,
            'confidence': forecast['confidence']
        }
    
    def _get_models(self):
        """Get different regression models to try"""
        return {
            'linear': LinearRegression(),
            'polynomial': make_pipeline(PolynomialFeatures(2), LinearRegression())
        }
    
    def _calculate_confidence(self, mae, std_dev):
        """Calculate confidence level based on model accuracy"""
        if std_dev == 0:
            return 'medium'
        
        relative_error = mae / std_dev if std_dev > 0 else 1
        
        if relative_error < 0.3:
            return 'high'
        elif relative_error < 0.6:
            return 'medium'
        else:
            return 'low'

def make_pipeline(*steps):
    """Simple pipeline implementation"""
    class Pipeline:
        def __init__(self, steps):
            self.steps = steps
        
        def fit(self, X, y):
            X_transformed = X
            for step in self.steps[:-1]:
                X_transformed = step.fit_transform(X_transformed)
            self.steps[-1].fit(X_transformed, y)
            return self
        
        def predict(self, X):
            X_transformed = X
            for step in self.steps[:-1]:
                X_transformed = step.transform(X_transformed)
            return self.steps[-1].predict(X_transformed)
    
    return Pipeline(steps)

# Global forecasting engine instance
forecasting_engine = ForecastingEngine()
