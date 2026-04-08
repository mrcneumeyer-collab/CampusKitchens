import streamlit as st
import psycopg2

st.set_page_config(page_title="Delete Food Entry", page_icon="🗑️")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🗑️ Delete a Food Entry")

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
        st.info("No entries available to delete.")
    else:
        entry_options = {
            f"ID {row[0]} | {row[1]} | {row[2]} | {row[3]} | Qty: {row[4]}": row[0]
            for row in rows
        }

        selected_label = st.selectbox("Select an entry to delete", list(entry_options.keys()))
        selected_id = entry_options[selected_label]

        confirm = st.checkbox("I confirm that I want to delete this entry.")

        if st.button("Delete Entry"):
            if confirm:
                try:
                    cur.execute("DELETE FROM food_entries_master WHERE id = %s;", (selected_id,))
                    conn.commit()
                    st.success(f"✅ Entry ID {selected_id} deleted successfully.")
                except Exception as e:
                    st.error(f"Error deleting entry: {e}")
            else:
                st.warning("Please confirm deletion first.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
