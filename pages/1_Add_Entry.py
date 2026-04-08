import streamlit as st
import psycopg2

st.set_page_config(page_title="Add Food Entry", page_icon="➕")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("➕ Add a New Food Entry")
st.write("Use the form below to add a new food entry to the database.")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Pull locations dynamically for dropdown
    cur.execute("""
        SELECT DISTINCT TRIM(location) AS location
        FROM "food_entries_master_cleaned (2)"
        WHERE location IS NOT NULL AND TRIM(location) <> ''
        ORDER BY location;
    """)
    location_results = cur.fetchall()
    location_options = [row[0] for row in location_results]

    if not location_options:
        st.warning("No locations found in the database.")
        st.stop()

    with st.form("add_entry_form"):
        entry_date = st.text_input("Date", placeholder="YYYY-MM-DD")
        location = st.selectbox("Location", location_options)
        item = st.text_input("Item")
        quantity = st.text_input("Quantity")

        submitted = st.form_submit_button("Add Entry")

        if submitted:
            entry_date = entry_date.strip() if entry_date else ""
            item = item.strip() if item else ""
            quantity = quantity.strip() if quantity else ""

            if entry_date and location and item and quantity:
                try:
                    cur.execute("""
                        INSERT INTO "food_entries_master_cleaned (2)" (date, location, item, quantity)
                        VALUES (%s, %s, %s, %s);
                    """, (entry_date, location, item, quantity))

                    conn.commit()
                    st.success(f"✅ Added {item} at {location} on {entry_date}")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error adding entry: {e}")
            else:
                st.warning("Please fill in all fields.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
