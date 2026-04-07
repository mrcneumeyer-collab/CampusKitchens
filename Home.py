import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(
    page_title="Food Entry Database App",
    page_icon="🍽️",
    layout="wide"
)

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB"])

st.title("🍽️ Food Entry Database App")
st.write("Welcome! Use the sidebar to view, add, edit, or delete food entries.")

st.markdown("---")
st.subheader("📊 Current Data Summary")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Overall summary metrics for the full table
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
    col3.metric("Unique Items", total_items)
    col4.metric("Total Quantity", total_quantity)

    st.markdown("---")
    st.subheader("🔍 Filter Food Entries")

    # Dynamic year options from the database
    cur.execute("""
        SELECT DISTINCT EXTRACT(YEAR FROM date) AS year
        FROM "food_entries_master_cleaned (2)"
        WHERE date IS NOT NULL
        ORDER BY year;
    """)
    year_results = cur.fetchall()
    year_options = ["All"] + [str(int(row[0])) for row in year_results if row[0] is not None]

    # Dynamic location options from the database
    # Any new location added later will appear automatically
    cur.execute("""
        SELECT DISTINCT TRIM(location) AS location
        FROM "food_entries_master_cleaned (2)"
        WHERE location IS NOT NULL AND TRIM(location) <> ''
        ORDER BY location;
    """)
    location_results = cur.fetchall()
    location_options = ["All"] + [row[0] for row in location_results]

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        year_filter = st.selectbox("Filter by Year", year_options)

    with filter_col2:
        location_filter = st.selectbox("Filter by Location", location_options)

    # Build filtered query
    query = """
        SELECT id, date, location, item, quantity
        FROM "food_entries_master_cleaned (2)"
        WHERE 1=1
    """
    params = []

    if year_filter != "All":
        query += " AND EXTRACT(YEAR FROM date) = %s"
        params.append(int(year_filter))

    if location_filter != "All":
        query += " AND TRIM(location) = %s"
        params.append(location_filter)

    query += " ORDER BY date ASC, id ASC;"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    st.markdown("---")
    st.subheader("📈 Filtered Data Summary")

    if rows:
        df = pd.DataFrame(
            rows,
            columns=["ID", "Date", "Location", "Item", "Quantity"]
        )

        df["Date"] = df["Date"].astype(str)
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)

        filtered_entries = len(df)
        filtered_total_quantity = df["Quantity"].sum()
        filtered_unique_items = df["Item"].nunique()
        filtered_unique_locations = df["Location"].nunique()

        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        sum_col1.metric("Filtered Entries", filtered_entries)
        sum_col2.metric("Filtered Unique Items", filtered_unique_items)
        sum_col3.metric("Filtered Locations", filtered_unique_locations)
        sum_col4.metric("Filtered Total Quantity", filtered_total_quantity)

        st.markdown("---")
        st.subheader("📋 Food Entries Table")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No food entries match the selected filters.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
