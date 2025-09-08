import streamlit as st
import pandas as pd
from datetime import datetime, time
from supabase import create_client

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

# --- connect to Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- interface ---
st.title("Drone Flight Log")

with st.form("flight_form"):
    date = st.date_input("Date", datetime.today())
    start = st.time_input("Start time", time(10,0))
    end = st.time_input("End time", time(11,0))
    project = st.text_input("Project number")
    pilot = st.selectbox("Pilot", ["Aleksandra Kruszewska", "Arnold Hoyer", "Bertalan Szabo-Papp", "Joao Scotti", "Michael Lloyd"])
    drone = st.selectbox("Drone", ["DJI Mini 3 - 1581F4XFC2285007E8MV", "DJI Mini 3 - Manchester", "DJI Mini 2", "DJI Mavic 3 Enterprise"])
    submit = st.form_submit_button("Save flight")

if submit:
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    duration = round((end_dt - start_dt).total_seconds() / 3600, 2)

    if duration <= 0:
        st.error("❌ End time must be later than start time.")
    else:
        date_str = date.strftime("%y-%m-%d")  # YY-MM-DD format
        supabase.table("flights").insert({
            "date": date_str,
            "start_time": str(start),
            "end_time": str(end),
            "duration": duration,
            "project": project,
            "pilot": pilot,
            "drone": drone
        }).execute()
        st.success(f"✅ Flight saved! Duration: {duration:.2f} hours")

# --- data preview with delete buttons ---
st.subheader("Logged flights (Admin)")

response = supabase.table("flights").select("*").execute()
rows = response.data
df = pd.DataFrame(rows)

if not df.empty:
    df["Duration (h)"] = df["duration"].map(lambda x: f"{x:.2f}")
    for _, row in df.iterrows():
        st.write(f"{row['date']} | {row['start_time']} - {row['end_time']} | {row['pilot']} | {row['drone']} | {row['Duration (h)']}h")
        if st.button("❌ Delete", key=f"del_{row['id']}"):
            supabase.table("flights").delete().eq("id", row["id"]).execute()
            st.experimental_rerun()

    # --- download CSV only ---
    st.download_button(
        label="⬇Download as CSV",
        data=df.drop(columns=["id"]).to_csv(index=False).encode("utf-8"),
        file_name="flights.csv",
        mime="text/csv"
    )

# --- statistics ---
st.subheader("Statistics")

if not df.empty:
    # total flight hours per pilot
    df_pilot = df.groupby("pilot").agg(
        Total_hours=("duration", lambda x: f"{x.sum():.2f}"),
        Flights=("id", "count")
    ).reset_index()
    st.write("Total flight hours per pilot:")
    st.table(df_pilot)

    # total flight hours per drone
    df_drone = df.groupby("drone").agg(
        Total_hours=("duration", lambda x: f"{x.sum():.2f}"),
        Flights=("id", "count")
    ).reset_index()
    st.write("Total flight hours per drone:")
    st.table(df_drone)
