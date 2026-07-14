import streamlit as st
import pandas as pd
import joblib
import requests
from datetime import date, datetime

# CONFIG

st.set_page_config(
    page_title="Prediksi Penyewaan Sepeda",
    page_icon="🚲",
    layout="centered"
)

# LOAD MODEL

@st.cache_resource
def load_model():
    return joblib.load("model_sepeda.pkl")

model = load_model()

API_LIMIT = date(2026, 7, 29)

@st.cache_data(ttl=600)
def get_weather(selected_date, selected_hour):

    today = date.today()

    if selected_date < today:

        base_url = "https://archive-api.open-meteo.com/v1/archive"

    else:

        base_url = "https://api.open-meteo.com/v1/forecast"

    url = (
        f"{base_url}"
        f"?latitude=36.3491"
        f"&longitude=127.3849"
        f"&start_date={selected_date}"
        f"&end_date={selected_date}"
        f"&hourly="
        "temperature_2m,"
        "relative_humidity_2m,"
        "dew_point_2m,"
        "wind_speed_10m,"
        "precipitation,"
        "snowfall,"
        "cloud_cover,"
        "visibility,"
        "shortwave_radiation"
        "&timezone=Asia/Seoul"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    return {

        "temperature":
        data["hourly"]["temperature_2m"][selected_hour],

        "humidity":
        data["hourly"]["relative_humidity_2m"][selected_hour],

        "dew_point":
        data["hourly"]["dew_point_2m"][selected_hour],

        "windspeed":
        data["hourly"]["wind_speed_10m"][selected_hour],

        "precipitation":
        data["hourly"]["precipitation"][selected_hour],

        "snowfall":
        data["hourly"]["snowfall"][selected_hour],

        "cloud_cover":
        data["hourly"]["cloud_cover"][selected_hour],

        "visibility":
        data["hourly"]["visibility"][selected_hour],

        "solar_radiation":
        data["hourly"]["shortwave_radiation"][selected_hour]

    }

# HEADER

st.title("🚲 Prediksi Penyewaan Sepeda")
st.markdown(
    """
    Prediksi jumlah penyewaan sepeda berdasarkan
    kondisi cuaca dan waktu.
    """
)

st.divider()

# INPUT TANGGAL

st.subheader("📅 Informasi Waktu")

tanggal = st.date_input(
    "Pilih Tanggal",
    value=date.today(),
    min_value=date(2017,1,1),
    max_value=date(2030,12,31)
)

hour = st.slider(
    "Jam",
    0,
    23,
    12
)

if tanggal <= API_LIMIT:
    weather = get_weather(tanggal, hour)

    if weather is None:
        st.error("❌ Gagal mengambil data cuaca.")
        st.stop()

    st.success("✅ Data cuaca berhasil diambil dari Open-Meteo.")

else:
    weather = None

    st.warning(
        "⚠️ Data cuaca untuk tanggal ini belum tersedia di Open-Meteo.\n"
        "Silakan masukkan data cuaca secara manual."
    )

# Feature otomatis
year = tanggal.year
month = tanggal.month
day_of_week = tanggal.weekday()

is_weekend = 1 if day_of_week >= 5 else 0

# hahhhhh
if weather:
    st.info(
        f"""
📍 Daejeon

📅 {tanggal}

🕒 {hour}:00

✅ Data cuaca diambil otomatis dari Open-Meteo.
"""
    )
else:
    st.info(
        f"""
📍 Daejeon

📅 {tanggal}

🕒 {hour}:00

✍️ Data cuaca dimasukkan secara manual.
"""
    )

# INPUT CUACA
st.subheader("🌦 Kondisi Cuaca")

col1, col2 = st.columns(2)

with col1:

    temperature = st.number_input(
    "Temperature (°C)",
    value=float(weather["temperature"]) if weather else 20.0)

    humidity = st.number_input(
    "Humidity (%)",
    min_value=0.0,
    max_value=100.0,
    value=float(weather["humidity"]) if weather else 60.0)

    windspeed = st.number_input(
    "Wind Speed (m/s)",
    value=float(weather["windspeed"]) if weather else 2.0)

    precipitation = st.number_input(
    "Precipitation",
    value=float(weather["precipitation"]) if weather else 0.0)

    sunshine = st.number_input(
    "Sunshine",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.1)

    snowfall = st.number_input(
    "Snowfall",
    value=float(weather["snowfall"]) if weather else 0.0)

with col2:

    dew_point = st.number_input(
    "Dew Point",
    value=float(weather["dew_point"]) if weather else 15.0)

    solar_radiation = st.number_input(
    "Solar Radiation",
    value=float(weather["solar_radiation"]) if weather else 300.0)

    cloud_cover = st.number_input(
    "Cloud Cover",
    value=float(weather["cloud_cover"]) if weather else 30.0)
    
    visibility = st.number_input(
    "Visibility",
    value=float(weather["visibility"]) if weather else 1500.0)

    ground_temp = st.number_input(
    "Ground Temperature",
    value=round(float(weather["temperature"]) + 2.97, 1) if weather else 23.0)

# HOLIDAY

st.subheader("🎉 Hari Libur")

holiday_text = st.selectbox(
    "Apakah Hari Libur?",
    ["Tidak", "Ya"]
)

holiday = 1 if holiday_text == "Ya" else 0

# PREDIKSI

if st.button("🔮 Prediksi"):

    input_data = pd.DataFrame({
        'temperature':[temperature],
        'precipitation':[precipitation],
        'windspeed':[windspeed],
        'humidity':[humidity],
        'dew_point':[dew_point],
        'sunshine':[sunshine],
        'solar_radiation':[solar_radiation],
        'snowfall':[snowfall],
        'cloud_cover':[cloud_cover],
        'visibility':[visibility],
        'ground_temp':[ground_temp],
        'holiday':[holiday],
        'year':[year],
        'month':[month],
        'day_of_week':[day_of_week],
        'hour':[hour],
        'is_weekend':[is_weekend]
    })

    prediksi = model.predict(input_data)[0]

    st.divider()

    st.subheader("📊 Hasil Prediksi")

    st.metric(
        label="Perkiraan Jumlah Penyewaan Sepeda",
        value=f"{round(prediksi):,}"
    )

    if prediksi < 500:
        st.error("Permintaan Sepeda Rendah 🚲")

    elif prediksi < 1500:
        st.warning("Permintaan Sepeda Sedang 🚲🚲")

    else:
        st.success("Permintaan Sepeda Tinggi 🚲🚲🚲")

    st.subheader("📋 Ringkasan Input")

    st.dataframe(input_data)