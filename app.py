import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
from io import BytesIO

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
st.title("✈️ Drone Flight Log")

with st.form("flight_form"):
    date = st.date_input("Date", datetime.today())
    start = st.time_input("Start time", time(10,0))
    end = st.time_input("End time", time(11,0))
    project = st.text_input("Project number")
    pilot = st.selectbox("Pilot", ["Aleksandra Kruszewska", "Arnold Hoyer", "Bertalan Szabo-Papp", "Joao Scotti"])
    drone = st.selectbox("Drone", ["DJI Mini 3", "DJI Mini 2", "DJI Mavic 3 Enterprise"])
    submit = st.form_submit_button("Save flight")

if submit:
    # calculate duration in hours
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    duration = (end_dt - start_dt).total_seconds() / 3600

    if duration <= 0:
        st.error("❌ End time must be later than start time.")
    else:
        c.execute("INSERT INTO flights (date, start_time, end_time, duration, project, pilot, drone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (str(date), str(start), str(end), duration, project, pilot, drone))
        conn.commit()
        st.success(f"✅ Flight saved! Duration: {duration:.2f} hours")

# --- data preview ---
st.subheader("📋 Logged flights")
rows = c.execute("SELECT date, start_time, end_time, duration, project, pilot, drone FROM flights").fetchall()
df = pd.DataFrame(rows, columns=["Date", "Start time", "End time", "Duration (h)", "Project", "Pilot", "Drone"])
st.table(df)

# --- download buttons ---
if not df.empty:
    st.download_button(
        label="⬇️ Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="flights.csv",
        mime="text/csv"
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Flights")
    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ Download as Excel",
        data=excel_data,
        file_name="flights.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- statistics ---
st.subheader("📊 Statistics")

# total flight hours per pilot
pilot_hours = c.execute("""
    SELECT pilot, ROUND(SUM(duration), 2) as total_hours, COUNT(*) as flights 
    FROM flights GROUP BY pilot
""").fetchall()
df_pilot = pd.DataFrame(pilot_hours, columns=["Pilot", "Total hours", "Flights"])
st.write("Total flight hours per pilot:")
st.table(df_pilot)

# total flight hours per drone
drone_hours = c.execute("""
    SELECT drone, ROUND(SUM(duration), 2) as total_hours, COUNT(*) as flights 
    FROM flights GROUP BY drone
""").fetchall()
df_drone = pd.DataFrame(drone_hours, columns=["Drone", "Total hours", "Flights"])
st.write("Total flight hours per drone:")
st.table(df_drone)
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
from io import BytesIO

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
st.title("✈️ Drone Flight Log")

with st.form("flight_form"):
    date = st.date_input("Date", datetime.today())
    start = st.time_input("Start time", time(10,0))
    end = st.time_input("End time", time(11,0))
    project = st.text_input("Project number")
    pilot = st.selectbox("Pilot", ["Aleksandra Kruszewska", "Arnold Hoyer", "Bertalan Szabo-Papp", "Joao Scotti"])
    drone = st.selectbox("Drone", ["DJI Mini 3", "DJI Mini 2", "DJI Mavic 3 Enterprise"])
    submit = st.form_submit_button("Save flight")

if submit:
    # calculate duration in hours
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    duration = (end_dt - start_dt).total_seconds() / 3600

    if duration <= 0:
        st.error("❌ End time must be later than start time.")
    else:
        c.execute("INSERT INTO flights (date, start_time, end_time, duration, project, pilot, drone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (str(date), str(start), str(end), duration, project, pilot, drone))
        conn.commit()
        st.success(f"✅ Flight saved! Duration: {duration:.2f} hours")

# --- data preview ---
st.subheader("📋 Logged flights")
rows = c.execute("SELECT date, start_time, end_time, duration, project, pilot, drone FROM flights").fetchall()
df = pd.DataFrame(rows, columns=["Date", "Start time", "End time", "Duration (h)", "Project", "Pilot", "Drone"])
st.table(df)

# --- download buttons ---
if not df.empty:
    st.download_button(
        label="⬇️ Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="flights.csv",
        mime="text/csv"
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Flights")
    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ Download as Excel",
        data=excel_data,
        file_name="flights.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- statistics ---
st.subheader("📊 Statistics")

# total flight hours per pilot
pilot_hours = c.execute("""
    SELECT pilot, ROUND(SUM(duration), 2) as total_hours, COUNT(*) as flights 
    FROM flights GROUP BY pilot
""").fetchall()
df_pilot = pd.DataFrame(pilot_hours, columns=["Pilot", "Total hours", "Flights"])
st.write("Total flight hours per pilot:")
st.table(df_pilot)

# total flight hours per drone
drone_hours = c.execute("""
    SELECT drone, ROUND(SUM(duration), 2) as total_hours, COUNT(*) as flights 
    FROM flights GROUP BY drone
""").fetchall()
df_drone = pd.DataFrame(drone_hours, columns=["Drone", "Total hours", "Flights"])
st.write("Total flight hours per drone:")
st.table(df_drone)
