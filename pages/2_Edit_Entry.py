import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Edit Food Entry", page_icon="✏️")

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB"])

st.title("✏️ Edit a Food Entry")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, date, location, item, quantity
        FROM "food_entries_master_cleaned (2)"
        ORDER BY date ASC, id ASC;
    """)
    rows = cur.fetchall()

    if not rows:
        st.info("No entries available.")
    else:
        entry_options = {
            f"ID {r[0]} | {r[1]} | {r[2]} | {r[3]} | Qty: {r[4]}": r
            for r in rows
        }

        selected = st.selectbox("Select entry", list(entry_options.keys()))
        entry = entry_options[selected]

        entry_id = entry[0]
        current_date = pd.to_datetime(entry[1]).date()
        current_location = entry[2]
        current_item = entry[3]
        current_quantity = float(entry[4])

        cur.execute("""
            SELECT DISTINCT TRIM(location)
            FROM "food_entries_master_cleaned (2)"
            WHERE location IS NOT NULL AND TRIM(location) <> ''
            ORDER BY location;
        """)
        existing_locations = [row[0] for row in cur.fetchall()]

        with st.form("edit_form"):
            new_date = st.date_input("Date", value=current_date)

            st.subheader("Location")
            location_choice = st.radio(
                "Choose location type:",
                ["Select existing location", "Enter new location"],
                key="edit_location_choice"
            )

            location_container = st.empty()

            if location_choice == "Select existing location":
                with location_container:
                    new_location = st.selectbox(
                        "Existing Locations",
                        existing_locations,
                        index=existing_locations.index(current_location) if current_location in existing_locations else 0,
                        key="edit_existing_location"
                    )
            else:
                with location_container:
                    new_location = st.text_input(
                        "New Location",
                        value=current_location,
                        key="edit_new_location"
                    )

            new_item = st.text_input("Item", value=current_item)
            new_quantity = st.number_input("Quantity", value=current_quantity)

            submitted = st.form_submit_button("Update")

            if submitted:
                new_location = new_location.strip()
                new_item = new_item.strip()

                if new_location and new_item:
                    cur.execute("""
                        UPDATE "food_entries_master_cleaned (2)"
                        SET date=%s, location=%s, item=%s, quantity=%s
                        WHERE id=%s;
                    """, (new_date, new_location, new_item, new_quantity, entry_id))

                    conn.commit()
                    st.success("✅ Updated successfully")
                    st.rerun()
                else:
                    st.warning("Fill all fields")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
