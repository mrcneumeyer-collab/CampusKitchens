import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Edit Food Entry", page_icon="✏️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("✏️ Edit a Food Entry")
st.write("Select an entry below and update its information.")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Pull all entries for selection
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
        current_location = selected_entry[2]
        current_item = selected_entry[3]
        current_quantity = str(selected_entry[4])

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

        location_index = location_options.index(current_location) if current_location in location_options else 0

        with st.form("edit_entry_form"):
            new_date = st.date_input("Date", value=current_date)
            new_location = st.selectbox("Location", location_options, index=location_index)
            new_item = st.text_input("Item", value=current_item)
            new_quantity = st.text_input("Quantity", value=current_quantity)

            submitted = st.form_submit_button("Update Entry")

            if submitted:
                new_item = new_item.strip() if new_item else ""
                new_quantity = new_quantity.strip() if new_quantity else ""

                if new_date and new_location and new_item and new_quantity:
                    try:
                        cur.execute("""
                            UPDATE "food_entries_master_cleaned (2)"
                            SET date = %s, location = %s, item = %s, quantity = %s
                            WHERE id = %s;
                        """, (new_date, new_location, new_item, new_quantity, entry_id))

                        conn.commit()
                        st.success(f"✅ Entry ID {entry_id} updated successfully.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error updating entry: {e}")
                else:
                    st.warning("Please fill in all fields.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
