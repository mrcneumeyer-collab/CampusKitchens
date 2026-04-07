import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Edit Food Entry", page_icon="✏️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("✏️ Edit a Food Entry")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, date, location, item, quantity
        FROM food_entries_master
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
        current_quantity = float(selected_entry[4])

        with st.form("edit_entry_form"):
            new_date = st.date_input("Date", value=current_date)
            new_location = st.text_input("Location", value=current_location)
            new_item = st.text_input("Item", value=current_item)
            new_quantity = st.number_input("Quantity", min_value=0.0, value=current_quantity, step=1.0)

            submitted = st.form_submit_button("Update Entry")

            if submitted:
                if new_location and new_item:
                    try:
                        cur.execute("""
                            UPDATE food_entries_master
                            SET date = %s, location = %s, item = %s, quantity = %s
                            WHERE id = %s;
                        """, (new_date, new_location, new_item, new_quantity, entry_id))

                        conn.commit()
                        st.success(f"✅ Entry ID {entry_id} updated successfully.")
                    except Exception as e:
                        st.error(f"Error updating entry: {e}")
                else:
                    st.warning("Please fill in all fields.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
