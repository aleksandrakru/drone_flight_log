import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
from io import BytesIO

st.set_page_config(page_title="Drone Flight Log", layout="centered")

# --- logo ---
st.image("logo.png", width=200)

# --- background ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f2f2
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- database ---
conn = sqlite3.connect("flights.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        duration REAL,
        project TEXT,
        pilot TEXT,
        drone TEXT
    )
''')
conn.commit()

# --- interface ---
st.title("Drone Flight Log")

with st.form("flight_form"):
    date = st.date_input("Date", datetime.today())
    start = st.time_input("Start time", time(10,0))
    end = st.time_input("End time", time(11,0))
    project = st.text_input("Project number")
    pilot = st.selectbox("Pilot", ["Aleksandra Kruszewska", "Arnold Hoyer", "Bertalan Szabo-Papp", "Joao Scotti"])
    drone = st.selectbox("Drone", ["DJI Mini 3", "DJI Mini 2", "DJI Mavic 3 Enterprise"])
    submit = st.form_submit_button("Save flight")

if submit:
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    duration = round((end_dt - start_dt).total_seconds() / 3600, 2)

    if duration <= 0:
        st.error("❌ End time must be later than start time.")
    else:
        date_str = date.strftime("%y-%m-%d")  # YY-MM-DD format
        c.execute(
            "INSERT INTO flights (date, start_time, end_time, duration, project, pilot, drone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (date_str, str(start), str(end), duration, project, pilot, drone)
        )
        conn.commit()
        st.success(f"✅ Flight saved! Duration: {duration:.2f} hours")

# --- data preview with delete buttons ---
st.subheader("Logged flights (Admin)")

rows = c.execute("SELECT id, date, start_time, end_time, duration, project, pilot, drone FROM flights").fetchall()
df = pd.DataFrame(rows, columns=["ID", "Date", "Start time", "End time", "Duration (h)", "Project", "Pilot", "Drone"])
df["Duration (h)"] = df["Duration (h)"].map(lambda x: f"{x:.2f}")  # zawsze 2 miejsca po przecinku

# wyświetlanie w jednej linii
for _, row in df.iterrows():
    st.write(f"{row['Date']} | {row['Start time']} - {row['End time']} | {row['Pilot']} | {row['Drone']} | {row['Duration (h)']}h")
    if st.button("❌ Delete", key=f"del_{row['ID']}"):
        c.execute("DELETE FROM flights WHERE id = ?", (row['ID'],))
        conn.commit()
        st.experimental_rerun()

# --- download CSV only ---
if not df.empty:
    st.download_button(
        label="⬇Download as CSV",
        data=df.drop(columns=["ID"]).to_csv(index=False).encode("utf-8"),
        file_name="flights.csv",
        mime="text/csv"
    )

# --- statistics ---
st.subheader("Statistics")

# total flight hours per pilot
pilot_hours = c.execute("""
    SELECT pilot, SUM(duration) as total_hours, COUNT(*) as flights 
    FROM flights GROUP BY pilot
""").fetchall()
df_pilot = pd.DataFrame(pilot_hours, columns=["Pilot", "Total hours", "Flights"])
df_pilot["Total hours"] = df_pilot["Total hours"].map(lambda x: f"{x:.2f}")
st.write("Total flight hours per pilot:")
st.table(df_pilot)

# total flight hours per drone
drone_hours = c.execute("""
    SELECT drone, SUM(duration) as total_hours, COUNT(*) as flights 
    FROM flights GROUP BY drone
""").fetchall()
df_drone = pd.DataFrame(drone_hours, columns=["Drone", "Total hours", "Flights"])
df_drone["Total hours"] = df_drone["Total hours"].map(lambda x: f"{x:.2f}")
st.write("Total flight hours per drone:")
st.table(df_drone)
