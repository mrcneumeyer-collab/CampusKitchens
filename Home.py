import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Food Entry Database App", page_icon="🍽️", layout="wide")

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB1"])

st.title("🍽️ Food Entry Database App")
st.write("Welcome! Use the sidebar to view, add, edit, or delete food entries.")

st.markdown("---")
st.subheader("📊 Current Data Summary")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM "food_entries_master_cleaned (2)";')
    total_entries = cur.fetchone()[0]

    cur.execute('SELECT COUNT(DISTINCT location) FROM "food_entries_master_cleaned (2)";')
    total_locations = cur.fetchone()[0]

    cur.execute('SELECT COUNT(DISTINCT item) FROM "food_entries_master_cleaned (2)";')
    total_items = cur.fetchone()[0]

    cur.execute('SELECT COALESCE(SUM(CAST(quantity AS NUMERIC)), 0) FROM "food_entries_master_cleaned (2)";')
    total_quantity = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Entries", total_entries)
    col2.metric("Locations", total_locations)
    col3.metric("Items", total_items)
    col4.metric("Total Quantity", total_quantity)

    st.markdown("---")
    st.subheader("📋 All Food Entries")

    cur.execute("""
        SELECT id, date, location, item, quantity
        FROM "food_entries_master_cleaned (2)"
        ORDER BY date ASC, id ASC;
    """)
    rows = cur.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Date", "Location", "Item", "Quantity"])
        df["Date"] = df["Date"].astype(str)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No food entries found.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
