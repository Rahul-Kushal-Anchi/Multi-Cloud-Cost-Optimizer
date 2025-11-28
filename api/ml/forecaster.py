"""
Cost Forecasting Model
Time series forecasting for AWS costs using Prophet
Predicts future costs with confidence intervals based on REAL historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

# Prophet import with fallback
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None

logger = logging.getLogger("api.ml.forecaster")


class CostForecaster:
    """
    Time series forecasting for AWS costs
    Uses Prophet for trend + seasonality modeling
    """
    
    def __init__(self):
        """Initialize cost forecaster"""
        if not PROPHET_AVAILABLE:
            logger.warning("Prophet not available, forecasting will use simple linear projection")
        self.model = None
        self.is_trained = False
        self.training_date = None
    
    def train(self, cost_data: pd.DataFrame) -> Dict[str, any]:
        """
        Train forecasting model on historical cost data
        
        Args:
            cost_data: DataFrame with columns [date, cost]
        
        Returns:
            Training summary
        """
        logger.info(f"Training forecaster on {len(cost_data)} days of data")
        
        if PROPHET_AVAILABLE:
            return self._train_prophet(cost_data)
        else:
            return self._train_simple(cost_data)
    
    def _train_prophet(self, cost_data: pd.DataFrame) -> Dict[str, any]:
        """Train using Prophet model"""
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        df = cost_data.copy()
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df['cost']
        df = df[['ds', 'y']].sort_values('ds')
        
        # Initialize and train Prophet
        self.model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True if len(df) > 365 else False,
            interval_width=0.95,  # 95% confidence intervals
        )
        
        self.model.fit(df)
        self.is_trained = True
        self.training_date = datetime.utcnow()
        
        logger.info("Prophet model trained successfully")
        
        return {
            "model_type": "Prophet",
            "training_samples": len(df),
            "earliest_date": df['ds'].min().strftime('%Y-%m-%d'),
            "latest_date": df['ds'].max().strftime('%Y-%m-%d'),
            "avg_daily_cost": float(df['y'].mean()),
            "training_date": self.training_date.isoformat(),
        }
    
    def _train_simple(self, cost_data: pd.DataFrame) -> Dict[str, any]:
        """Train using simple linear regression (fallback)"""
        df = cost_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Store for simple forecasting
        self.training_data = df
        self.is_trained = True
        self.training_date = datetime.utcnow()
        
        return {
            "model_type": "Simple Linear",
            "training_samples": len(df),
            "avg_daily_cost": float(df['cost'].mean()),
            "training_date": self.training_date.isoformat(),
        }
    
    def forecast(self, periods: int = 30) -> List[Dict[str, any]]:
        """
        Generate cost forecast
        
        Args:
            periods: Number of days to forecast
        
        Returns:
            List of forecasts with date, cost, confidence bounds
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before forecasting")
        
        logger.info(f"Generating {periods}-day forecast")
        
        if PROPHET_AVAILABLE and self.model:
            return self._forecast_prophet(periods)
        else:
            return self._forecast_simple(periods)
    
    def _forecast_prophet(self, periods: int) -> List[Dict[str, any]]:
        """Forecast using Prophet"""
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods)
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract forecast for future periods only
        forecast_future = forecast.tail(periods)
        
        results = []
        for _, row in forecast_future.iterrows():
            results.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "forecasted_cost": float(row['yhat']),
                "confidence_lower": float(row['yhat_lower']),
                "confidence_upper": float(row['yhat_upper']),
                "trend": "increasing" if row['trend'] > 0 else "decreasing",
            })
        
        return results
    
    def _forecast_simple(self, periods: int) -> List[Dict[str, any]]:
        """Simple linear projection forecast"""
        df = self.training_data
        
        # Calculate trend
        df['days'] = (df['date'] - df['date'].min()).dt.days
        
        # Simple linear regression
        x = df['days'].values
        y = df['cost'].values
        
        # Calculate slope and intercept
        slope = np.polyfit(x, y, 1)[0]
        intercept = np.polyfit(x, y, 1)[1]
        
        # Generate forecasts
        last_date = df['date'].max()
        last_day = df['days'].max()
        
        results = []
        for i in range(1, periods + 1):
            forecast_date = last_date + timedelta(days=i)
            forecast_day = last_day + i
            forecast_cost = slope * forecast_day + intercept
            
            # Simple confidence interval (±10%)
            lower = forecast_cost * 0.9
            upper = forecast_cost * 1.1
            
            results.append({
                "date": forecast_date.strftime('%Y-%m-%d'),
                "forecasted_cost": float(max(0, forecast_cost)),
                "confidence_lower": float(max(0, lower)),
                "confidence_upper": float(max(0, upper)),
                "trend": "increasing" if slope > 0 else "decreasing",
            })
        
        return results
    
    def get_forecast_summary(self, periods: int = 30) -> Dict[str, any]:
        """
        Get forecast summary with key metrics
        
        Args:
            periods: Number of days to forecast
        
        Returns:
            Summary with total forecasted cost, trend, etc.
        """
        forecast_data = self.forecast(periods)
        
        total_forecasted = sum(f['forecasted_cost'] for f in forecast_data)
        avg_daily_forecasted = total_forecasted / len(forecast_data) if forecast_data else 0
        
        # Calculate trend
        if len(forecast_data) >= 2:
            first_week_avg = np.mean([f['forecasted_cost'] for f in forecast_data[:7]])
            last_week_avg = np.mean([f['forecasted_cost'] for f in forecast_data[-7:]])
            trend_pct = ((last_week_avg - first_week_avg) / first_week_avg * 100) if first_week_avg > 0 else 0
        else:
            trend_pct = 0
        
        return {
            "forecast_period_days": periods,
            "total_forecasted_cost": round(total_forecasted, 2),
            "avg_daily_forecasted_cost": round(avg_daily_forecasted, 2),
            "trend": "increasing" if trend_pct > 5 else "decreasing" if trend_pct < -5 else "stable",
            "trend_percentage": round(trend_pct, 1),
            "forecasts": forecast_data,
        }


# Singleton instance
cost_forecaster = CostForecaster()

