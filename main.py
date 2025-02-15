# main.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils import load_data, save_data, calculate_bill, init_db, delete_record, update_record
from flask import Flask
from models import db

# Initialize Flask app for database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
with app.app_context():
    init_db(app)

# Streamlit Page Configuration
st.set_page_config(
    page_title="Utility Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Navigation
st.sidebar.title("Navigation")


# Initialize session state for data
with app.app_context():
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

# Page Title
st.title("📊 Utility Expense Tracker")
st.markdown("""
Track your monthly electricity consumption and rent expenses.

📝 **Calculation Method**:
1. Units Consumed = Current Reading - Previous Reading
2. Electricity Cost = Units × Rate per Unit
3. Total Cost = Electricity Cost + Monthly Rent
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    electricity_rate = st.number_input(
        "Electricity Rate (रु/unit)",
        min_value=0.0,
        value=12.0,
        step=0.1
    )
    rent_amount = st.number_input(
        "Monthly Rent (रु)",
        min_value=0,
        value=12000,
        step=100
    )

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Monthly Reading Entry")

    # 🟡 Get Previous Reading (Allow Manual Input if First Entry)
    if st.session_state.data.empty:
        prev_reading = st.number_input(
            "Enter Previous Reading (First Entry Only)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            help="Since this is your first entry, please provide the previous meter reading."
        )
    else:
        prev_reading = float(st.session_state.data['current_reading'].iloc[-1])

    prev_reading_display = st.number_input(
        "Previous Reading",
        value=prev_reading,
        disabled=not st.session_state.data.empty,  # Disable input if data exists
        step=0.1
    )


    # Input Form
    with st.form("reading_form"):
        # Fix: Use an accepted date format (e.g., YYYY/MM/DD)
        reading_date = st.date_input(
            "Select Month (Year-Month)",
            value=datetime.today()
        )

        # # Extract only the month and year from the selected date
        # month_year = reading_date.strftime("%Y-%m")
        
        # Store full date (YYYY-MM-DD)
        full_date = reading_date.strftime("%Y-%m-%d")  # e.g., 2025-02-16
        month_year = full_date  # Use full_date for storage


        prev_reading_display = st.number_input(
            "Previous Reading",
            value=prev_reading,
            disabled=True
        )

        current_reading = st.number_input(
            "Current Reading",
            min_value=prev_reading,
            value=prev_reading,
            step=0.1
        )

        if current_reading > prev_reading:
            st.write("### Calculation Preview")
            bill = calculate_bill(
                current_reading=current_reading,
                previous_reading=prev_reading,
                rate_per_unit=electricity_rate,
                monthly_rent=rent_amount
            )
            st.write(f"Units Consumed: {bill['units_consumed']} units")
            st.write(f"Electricity Cost: रु{bill['electricity_cost']:.2f}")
            st.write(f"Total Monthly Cost (with Rent): रु{bill['total_cost']:.2f}")

        submitted = st.form_submit_button("Calculate & Save")

        if submitted:
            with app.app_context():
                if not st.session_state.data.empty and month_year in st.session_state.data['month'].values:
                    st.error(f"An entry for {month_year} already exists!")
                elif current_reading <= prev_reading:
                    st.error("Current reading must be greater than previous reading!")
                else:
                    bill = calculate_bill(
                        current_reading=current_reading,
                        previous_reading=prev_reading,
                        rate_per_unit=electricity_rate,
                        monthly_rent=rent_amount
                    )

                    new_entry = pd.DataFrame({
                        'month': [month_year],
                        'previous_reading': [prev_reading],
                        'current_reading': [current_reading],
                        'consumption': [bill['units_consumed']],
                        'electricity_cost': [bill['electricity_cost']],
                        'rent': [rent_amount],
                        'total_cost': [bill['total_cost']]
                    })

                    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
                    save_data(st.session_state.data)
                    st.success("Entry saved successfully!")

with col2:
    st.subheader("📊 Current Month Summary")
    if not st.session_state.data.empty:
        latest = st.session_state.data.iloc[-1]
        st.metric("Electricity Consumption", f"{latest['consumption']:.1f} units")
        st.metric("Electricity Cost", f"रु{latest['electricity_cost']:.2f}")
        st.metric("Rent", f"रु{latest['rent']:.2f}")
        st.metric("Total Cost", f"रु{latest['total_cost']:.2f}")

# Historical Data
st.subheader("📈 Historical Data")
tab1, tab2 = st.tabs(["Table View", "Trend Analysis"])

with tab1:
    if not st.session_state.data.empty:
        st.dataframe(
            st.session_state.data.style.format({
                'month': lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%Y-%m-%d"),  # Show full date format
                'electricity_cost': 'रु{:.2f}',
                'rent': 'रु{:.2f}',
                'total_cost': 'रु{:.2f}',
                'consumption': '{:.1f}',
                'previous_reading': '{:.1f}',
                'current_reading': '{:.1f}'
            }),
            hide_index=True
        )

with tab2:
    if not st.session_state.data.empty:
        fig1 = px.line(
            st.session_state.data,
            x='month',
            y='consumption',
            title='Monthly Consumption Trend'
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(
            st.session_state.data,
            x='month',
            y=['electricity_cost', 'rent'],
            title='Monthly Cost Breakdown',
            labels={'value': 'Cost (रु)', 'variable': 'Category'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        
st.subheader("✏️ Modify or Delete Record")

if not st.session_state.data.empty:
    # Step 1: Select Record
    selected_month = st.selectbox(
        "Select Month to Modify",
        options=st.session_state.data['month'].unique(),
        format_func=lambda x: f"{x} (Existing Record)"
    )
    
    # Step 2: Display Selected Record
    record = st.session_state.data[
        st.session_state.data['month'] == selected_month
    ].iloc[0]

    updated_previous = st.number_input(
        "Previous Reading", 
        value=record['previous_reading']
    )
    updated_current = st.number_input(
        "Current Reading", 
        value=record['current_reading']
    )
    updated_consumption = st.number_input(
        "Consumption", 
        value=record['consumption']
    )
    updated_electricity_cost = st.number_input(
        "Electricity Cost (₹)", 
        value=record['electricity_cost']
    )
    updated_rent = st.number_input(
        "Monthly Rent (₹)", 
        value=record['rent']
    )
    updated_total_cost = st.number_input(
        "Total Cost (₹)", 
        value=record['total_cost']
    )

    # Step 3: Save or Delete Options
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes"):
            success = update_record(
                app,  # Pass app context
                month=selected_month,
                previous_reading=updated_previous,
                current_reading=updated_current,
                consumption=updated_consumption,
                electricity_cost=updated_electricity_cost,
                rent=updated_rent,
                total_cost=updated_total_cost
            )
            if success:
                st.success(f"Record for {selected_month} updated successfully!")
            else:
                st.error("Failed to update the record.")

    
    with col2:
        if st.button("🗑️ Delete Record"):
            success = delete_record(app, selected_month)  # Pass app context
            if success:
                st.success(f"Record for {selected_month} deleted successfully!")
            else:
                st.error("Failed to delete the record.")
else:
    st.info("No records found to modify.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8501))
    st.write(f"App is running on port {port}")
