import streamlit as st
import psycopg2

st.set_page_config(page_title="Add Food Entry", page_icon="➕")

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB"])

st.title("➕ Add a New Food Entry")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT TRIM(location) AS location
        FROM "food_entries_master_cleaned (2)"
        WHERE location IS NOT NULL AND TRIM(location) <> ''
        ORDER BY location;
    """)
    existing_locations = [row[0] for row in cur.fetchall()]

    with st.form("add_entry_form"):
        entry_date = st.date_input("Date")

        st.subheader("Location")
        location_choice = st.radio(
            "Choose how to enter the location:",
            ["Select existing location", "Enter new location"],
            key="add_location_choice"
        )

        location_container = st.empty()

        if location_choice == "Select existing location":
            with location_container:
                if existing_locations:
                    location = st.selectbox(
                        "Existing Locations",
                        existing_locations,
                        key="add_existing_location"
                    )
                else:
                    location = st.text_input(
                        "New Location",
                        key="add_new_location_fallback"
                    )
        else:
            with location_container:
                location = st.text_input(
                    "New Location",
                    key="add_new_location"
                )

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
                    st.success(f"✅ Added {item} at {location}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill all fields.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
