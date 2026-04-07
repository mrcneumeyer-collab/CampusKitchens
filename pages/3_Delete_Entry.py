import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Delete Food Entry", page_icon="🗑️")

def get_connection():
    return psycopg2.connect(st.secrets["URL_DB"])

st.title("🗑️ Delete a Food Entry")
st.write("Select an existing entry from the live database and delete it.")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Pull entries dynamically so new years, locations, and items always appear
    cur.execute("""
        SELECT id, date, location, item, quantity
        FROM "food_entries_master_cleaned (2)"
        ORDER BY date ASC, id ASC;
    """)
    rows = cur.fetchall()

    if not rows:
        st.info("No entries available to delete.")
    else:
        df = pd.DataFrame(rows, columns=["ID", "Date", "Location", "Item", "Quantity"])
        df["Date"] = df["Date"].astype(str)

        entry_options = {
            f"ID {row[0]} | {row[1]} | {row[2]} | {row[3]} | Qty: {row[4]}": row[0]
            for row in rows
        }

        selected_label = st.selectbox("Select an entry to delete", list(entry_options.keys()))
        selected_id = entry_options[selected_label]

        st.markdown("### Entry Preview")
        preview_row = df[df["ID"] == selected_id]
        st.dataframe(preview_row, use_container_width=True)

        confirm = st.checkbox("I confirm that I want to permanently delete this entry.")

        if st.button("Delete Entry"):
            if confirm:
                try:
                    cur.execute("""
                        DELETE FROM "food_entries_master_cleaned (2)"
                        WHERE id = %s;
                    """, (selected_id,))
                    conn.commit()
                    st.success(f"✅ Entry ID {selected_id} deleted successfully.")
                    st.info("Refresh or revisit the page to see updated entries.")
                except Exception as e:
                    st.error(f"Error deleting entry: {e}")
            else:
                st.warning("Please confirm deletion before deleting the entry.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")
