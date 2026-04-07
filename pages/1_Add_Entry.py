import streamlit as st
import psycopg2

st.set_page_config(page_title="Add Food Entry", page_icon="➕")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("➕ Add a New Food Entry")

with st.form("add_entry_form"):
    entry_date = st.date_input("Date")
    location = st.text_input("Location")
    item = st.text_input("Item")
    quantity = st.number_input("Quantity", min_value=0.0, step=1.0)

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if location and item:
            try:
                conn = get_connection()
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO food_entries_master (date, location, item, quantity)
                    VALUES (%s, %s, %s, %s);
                """, (entry_date, location, item, quantity))

                conn.commit()
                cur.close()
                conn.close()

                st.success(f"✅ Added {item} at {location} on {entry_date}")
            except Exception as e:
                st.error(f"Error adding entry: {e}")
        else:
            st.warning("Please fill in all fields.")
