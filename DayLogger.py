
import streamlit as st
from datetime import datetime
import pandas as pd
import sqlite3
from contextlib import closing

# Initialize connection to SQLite database and create table if it doesn't exist
def init_db(db_path='office_visits.db'):
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS office_visits
                             (date TEXT PRIMARY KEY)''')
            conn.commit()

# Load data from the SQLite database
def load_data(db_path='office_visits.db'):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM office_visits", conn)

# Add a new office visit entry
def add_entry(date, db_path='office_visits.db'):
    try:
        with sqlite3.connect(db_path) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("INSERT INTO office_visits (date) VALUES (?)", (date,))
                conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Delete an office visit entry
def enhanced_delete_entry(date, db_path='office_visits.db'):
    try:
        with sqlite3.connect(db_path) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("DELETE FROM office_visits WHERE date = ?", (date,))
                conn.commit()
        return True
    except Exception as e:
        st.error(f"Failed to delete the entry: {e}")
        return False

# Get the number of office visits in the current month
def get_current_month_visits_optimized(data):
    current_month = pd.to_datetime('now').month
    current_year = pd.to_datetime('now').year
    filtered_data = data[(data['date_dt'].dt.month == current_month) & (data['date_dt'].dt.year == current_year)]
    return len(filtered_data)

def main():
    st.title("DayLogger")

    # Initialize and load data
    db_path = 'office_visits.db'
    init_db(db_path)
    data = load_data(db_path)
    data['date_dt'] = pd.to_datetime(data['date'])

    # Display current month overview
    current_month_visits = get_current_month_visits_optimized(data)
    st.header(f"Office Visits This Month: {current_month_visits}")

    # Add entry form
    st.subheader("Log Office Visit")
    visit_date = st.date_input("Select Date")
    if st.button("Log Visit"):
        if add_entry(visit_date.strftime('%Y-%m-%d'), db_path):
            st.success("Office visit logged successfully!")
            st.experimental_rerun()
        else:
            st.warning("An office visit entry already exists for the selected date.")

    # History and deletion
    st.subheader("Office Visit History")
    if len(data) > 0:
        for i, row in data.iterrows():
            col1, col2, col3 = st.columns([0.45, 0.45, 0.1])
            with col1:
                st.text(row['date'])
            with col2:
                weekday = row['date_dt'].strftime('%A')  # Calculate the weekday
                st.text(weekday)
            with col3:
                if st.button("🗑️", key=f"delete_{row['date']}"):
                    if enhanced_delete_entry(row['date'], db_path):
                        st.success("Entry deleted successfully.")
                        st.experimental_rerun()
    else:
        st.info("No office visits logged yet.")

if __name__ == "__main__":
    main()
