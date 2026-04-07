import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Edit Food Entry", page_icon="✏️")

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB"])

st.title("✏️ Edit a Food Entry")
st.write("Update an existing food entry using a current or new location.")

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
        st.info("No entries available to edit.")
    else:
        entry_options = {
            f"ID {row[0]} | {row[1]} | {row[2]} | {row[3]} | Qty: {row[4]}": row
            for row in rows
        }

        selected_label = st.selectbox("Select an entry to edit", list(entry_options.keys()))
        selected_entry = entry_options[selected_label]

        entry_id = selected_entry[0]
        current_date = pd.to_datetime(selected_entry[1]).date()
        current_location = selected_entry[2].strip() if selected_entry[2] else ""
        current_item = selected_entry[3]
        current_quantity = float(selected_entry[4])

        cur.execute("""
            SELECT DISTINCT TRIM(location) AS location
            FROM "food_entries_master_cleaned (2)"
            WHERE location IS NOT NULL AND TRIM(location) <> ''
            ORDER BY location;
        """)
        location_results = cur.fetchall()
        existing_locations = [row[0] for row in location_results]

        with st.form("edit_entry_form"):
            new_date = st.date_input("Date", value=current_date)

            st.subheader("Location")
            location_choice = st.radio(
                "Choose how to update the location:",
                ["Select existing location", "Enter new location"]
            )

            if location_choice == "Select existing location":
                if existing_locations:
                    default_index = existing_locations.index(current_location) if current_location in existing_locations else 0
                    new_location = st.selectbox(
                        "Existing Locations",
                        existing_locations,
                        index=default_index
                    )
                else:
                    st.warning("No existing locations found. Please enter a new location below.")
                    new_location = st.text_input("New Location", value=current_location)
            else:
                new_location = st.text_input("New Location", value=current_location)

            new_item = st.text_input("Item", value=current_item)
            new_quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                value=current_quantity,
                step=1.0
            )

            submitted = st.form_submit_button("Update Entry")

            if submitted:
                new_location = new_location.strip() if new_location else ""
                new_item = new_item.strip() if new_item else ""

                if new_location and new_item:
                    try:
                        cur.execute("""
                            UPDATE "food_entries_master_cleaned (2)"
                            SET date = %s,
                                location = %s,
                                item = %s,
                                quantity = %s
                            WHERE id = %s;
                        """, (new_date, new_location, new_item, new_quantity, entry_id))

                        conn.commit()
                        st.success(f"✅ Entry ID {entry_id} updated successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating entry: {e}")
                else:
                    st.warning("Please fill in both the location and item fields.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
