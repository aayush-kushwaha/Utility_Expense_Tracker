# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class ExpenseRecord(db.Model):
    """Database model for storing utility expense records."""
    __tablename__ = 'expense_records'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(10), unique=True, nullable=False)  # Format: YYYY-MM
    previous_reading = db.Column(db.Float, nullable=False)
    current_reading = db.Column(db.Float, nullable=False)
    consumption = db.Column(db.Float, nullable=False)
    electricity_cost = db.Column(db.Float, nullable=False)
    rent = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExpenseRecord {self.month}: ₹{self.total_cost}>'
