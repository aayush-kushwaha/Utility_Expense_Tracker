# utils.py
import pandas as pd
from models import db, ExpenseRecord
from init_db import app  # Import app from init_db.py
# utils.py
from flask import current_app

def update_record(app, month, previous_reading, current_reading, consumption, electricity_cost, rent, total_cost):
    """Update an expense record with proper app context."""
    try:
        with app.app_context():
            record = ExpenseRecord.query.filter_by(month=month).first()
            if record:
                record.previous_reading = previous_reading
                record.current_reading = current_reading
                record.consumption = consumption
                record.electricity_cost = electricity_cost
                record.rent = rent
                record.total_cost = total_cost
                db.session.commit()
                return True
            return False
    except Exception as e:
        db.session.rollback()
        print(f"Error updating record: {e}")
        return False



def delete_record(app, month):
    """Delete an expense record with proper app context."""
    try:
        with app.app_context():
            record = ExpenseRecord.query.filter_by(month=month).first()
            if record:
                db.session.delete(record)
                db.session.commit()
                return True
            return False
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting record: {e}")
        return False



def calculate_bill(current_reading, previous_reading, rate_per_unit, monthly_rent):
    """Calculate total monthly cost (electricity + rent) using correct logic."""
    if current_reading < previous_reading:
        raise ValueError("Current reading cannot be less than previous reading!")

    # Step 1: Units Consumed
    units_consumed = current_reading - previous_reading

    # Step 2: Electricity Cost
    electricity_cost = units_consumed * rate_per_unit

    # Step 3: Total Monthly Cost
    total_cost = electricity_cost + monthly_rent

    return {
        "units_consumed": units_consumed,
        "electricity_cost": electricity_cost,
        "total_cost": total_cost
    }

def load_data():
    """Load all expense records from the database into a pandas DataFrame."""
    records = ExpenseRecord.query.all()
    return pd.DataFrame([{
        'month': record.month,
        'previous_reading': record.previous_reading,
        'current_reading': record.current_reading,
        'consumption': record.consumption,
        'electricity_cost': record.electricity_cost,
        'rent': record.rent,
        'total_cost': record.total_cost
    } for record in records])

def save_data(data):
    """Save monthly expense data into the database."""
    for _, row in data.iterrows():
        if not ExpenseRecord.query.filter_by(month=row['month']).first():
            record = ExpenseRecord(
                month=row['month'],
                previous_reading=row['previous_reading'],
                current_reading=row['current_reading'],
                consumption=row['consumption'],
                electricity_cost=row['electricity_cost'],
                rent=row['rent'],
                total_cost=row['total_cost']
            )
            db.session.add(record)
    db.session.commit()

def init_db(app):
    """Initialize database with Flask app context."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
