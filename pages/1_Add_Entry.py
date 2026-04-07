import streamlit as st
import psycopg2

st.set_page_config(page_title="Add Food Entry", page_icon="➕")

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB"])

st.title("➕ Add a New Food Entry")
st.write("Add a new food record using an existing location or create a new one.")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Get current locations dynamically from the database
    cur.execute("""
        SELECT DISTINCT TRIM(location) AS location
        FROM "food_entries_master_cleaned (2)"
        WHERE location IS NOT NULL AND TRIM(location) <> ''
        ORDER BY location;
    """)
    location_results = cur.fetchall()
    existing_locations = [row[0] for row in location_results]

    with st.form("add_entry_form"):
        entry_date = st.date_input("Date")

        st.subheader("Location")
        location_choice = st.radio(
            "Choose how to enter the location:",
            ["Select existing location", "Enter new location"]
        )

        if location_choice == "Select existing location":
            if existing_locations:
                location = st.selectbox("Existing Locations", existing_locations)
            else:
                st.warning("No existing locations found. Please enter a new location.")
                location = st.text_input("New Location")
        else:
            location = st.text_input("New Location")

        item = st.text_input("Item")
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0)

        submitted = st.form_submit_button("Add Entry")

        if submitted:
            location = location.strip() if location else ""
            item = item.strip() if item else ""

            if location and item:
                try:
                    cur.execute("""
                        INSERT INTO "food_entries_master_cleaned (2)" (date, location, item, quantity)
                        VALUES (%s, %s, %s, %s);
                    """, (entry_date, location, item, quantity))

                    conn.commit()
                    st.success(f"✅ Added {item} at {location} on {entry_date}")
                    st.info("Refresh or revisit the page to see the updated location list.")
                except Exception as e:
                    st.error(f"Error adding entry: {e}")
            else:
                st.warning("Please fill in both the location and item fields.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
