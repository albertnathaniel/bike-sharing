import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import datetime
sns.set(style='white')

st.set_page_config(
    page_title="Bike Rental Dashboard - Albert Nathaniel",
    page_icon="bike-rental.png",
    layout="centered"
)

# Membuat fungsi create_rent_casual
def create_rent_casual(df):
    rent_casual = df.groupby(by="dteday").agg({
        "casual": "sum"
    }).reset_index()
    return rent_casual

# Membuat fungsi create_rent_registered
def create_rent_registered(df):
    rent_registered = df.groupby(by="dteday").agg({
        "registered": "sum"
    }).reset_index()
    return rent_registered

# Membuat fungsi create_rent_count
def create_rent_count(df):
    rent_count = df.groupby(by="dteday").agg({
        "cnt": "sum"
    }).reset_index()
    return rent_count

# Membaca file dataset bike_rental.csv
bike_rental_df = pd.read_csv("data/bike_rental.csv")

datetime_columns = ["dteday"]
bike_rental_df.sort_values(by="dteday", inplace=True)
bike_rental_df.reset_index(inplace=True)

for column in datetime_columns:
    bike_rental_df[column] = pd.to_datetime(bike_rental_df[column])

min_date = bike_rental_df["dteday"].min()
max_date = bike_rental_df["dteday"].max()

# Membuat sidebar
with st.sidebar:
    st.image("bike-rental.png", width=200)
    
    try:
        start_date, end_date = st.date_input(
            label="Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError as e:
        st.error("Harap pilih rentang waktu yang valid, bukan hanya satu tanggal.")
        st.stop()  # Menghentikan eksekusi lebih lanjut jika terjadi kesalahan

# Menyimpan data yang telah difilter
main_df = bike_rental_df[(bike_rental_df["dteday"] >= str(start_date)) & 
                (bike_rental_df["dteday"] <= str(end_date))]

# Menyimpan Dataframe dari fungsi yang telah dibuat
count_df = create_rent_count(main_df)
casual_df = create_rent_casual(main_df)
registered_df = create_rent_registered(main_df)

# Mengatur Tema Grafik
theme = st.sidebar.selectbox("Tema Grafik", ["Mode Cerah", "Mode Gelap"])
if theme == "Mode Cerah":
    plt.style.use('default')
else:
    plt.style.use('dark_background')

# Membuat Visualisasi Data pada Dashboard
st.header("Bike Rental Dashboard :bike:")

st.subheader("Informasi Pengguna Rental")

col1, col2, col3 = st.columns(3)

with col1:
    rent_casual = casual_df["casual"].sum()
    rent_casual_formatted = "{:,.0f}".format(rent_casual)
    st.metric("Pengguna Kasual", value=rent_casual_formatted)

with col2:
    rent_registered = registered_df["registered"]. sum()
    rent_registered_formatted = "{:,.0f}".format(rent_registered)
    st.metric("Pengguna Teregistrasi", value=rent_registered_formatted)

with col3:
    rent_count = count_df["cnt"].sum()
    rent_count_formatted = "{:,.0f}".format(rent_count)
    st.metric("Total pengguna", value=rent_count_formatted)

fig, ax = plt.subplots(figsize=(12, 6))

# Visualisasi perbandingan registered bike pada weekday
sns.lineplot(
    x="weekday", 
    y="registered",
    data=main_df,
    color='blue',
    label='Teregistrasi'
)

# Visualisasi perbandingan casual bike pada weekday
sns.lineplot(
    x="weekday", 
    y="casual",
    data=main_df,
    color='green',
    label='Kasual'
)

# Visualisasi perbandingan total rental bike pada weekday
sns.lineplot(
    x="weekday", 
    y="cnt",
    data=main_df,
    color='orange',
    label='Total Pengguna'
)

plt.xlabel("Hari")
plt.ylabel("Jumlah Rental Sepeda")
plt.legend(title="Tipe Pengguna", loc="best")
plt.tight_layout()
plt.grid(True)

st.pyplot(fig)

with st.expander('Keterangan'):
        st.write(
            """
            `casual`: Jumlah pengguna rental sepeda yang bersifat tidak teratur atau tidak berlangganan.     
            `registered`: Jumlah pengguna rental sepeda yang terdaftar atau berlangganan.    
            `cnt`: Jumlah total rental sepeda, termasuk pengguna sewa sepeda kasual maupun yang teregistrasi.  
            """
        )

# === VISUALISASI RFM === 
st.subheader("Segmentasi Pengguna Terbaik Menggunakan RFM Analysis")  

# Hitung recency (hari sejak terakhir transaksi)
main_df["recency"] = (main_df["dteday"].max() - main_df["dteday"]).dt.days

# Hitung frequency (jumlah transaksi)
main_df["frequency"] = main_df.groupby("cnt")["cnt"].transform("count")

# Hitung monetary (total nilai transaksi)
main_df["monetary"] = main_df["cnt"] * main_df["registered"]

# Analisis RFM
rfm_data = main_df[["instant", "recency", "frequency", "monetary"]]

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_data.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_data.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_data.monetary.mean(), "USD", locale="en_US") 
    st.metric("Average Monetary", value=avg_monetary)

fig, axes = plt.subplots(1, 3, figsize=(21, 9))

# Visualisasi Distribusi Recency
sns.boxplot(y=rfm_data["recency"], ax=axes[0], color="lightblue")
axes[0].set_ylabel("Recency (days)")
axes[0].set_title("Recency Distribution")

# Visualisasi Distribusi Frekuensi
sns.violinplot(y=rfm_data["frequency"], ax=axes[1], color="lightgreen")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Frequency Distribution")

# Visualisasi Distribusi Monetary
sns.histplot(rfm_data["monetary"], bins=20, color="orange", edgecolor="black", ax=axes[2], kde=True)
axes[2].set_xlabel("Monetary Value")
axes[2].set_ylabel("Count")
axes[2].set_title("Monetary Distribution")

plt.tight_layout()
st.pyplot(fig)

with st.expander('Keterangan'):
        st.write(
            """
            `Recency`: Ukuran seberapa baru terakhir kali pelanggan melakukan transaksi.  
            `Frequency`: Ukuran seberapa sering pelanggan melakukan transaksi dalam periode waktu tertentu.   
            `Monetary`: Total nilai pembelian atau pengeluaran yang dilakukan oleh pelanggan dalam periode waktu tertentu.    
            """
        )

# === VISUALISASI Trend Jumlah total rental bike 2011 dan 2012 ===
st.subheader("Tren Rental Sepeda Berdasarkan Rentang Waktu")

main_df["mnth"] = pd.Categorical(main_df["mnth"], categories=
    ["January","February","March","April","May","June","July","August","September","October","November","December"],
    ordered=True)

bike_month = main_df.groupby(by=["yr", "mnth"], observed=False).agg({
    "cnt": "sum"
})

fig = plt.figure(figsize=(10, 6))
sns.lineplot(
    data=bike_month,
    x="mnth",
    y="cnt",
    hue="yr",
    palette="bright",
    marker="o"
)
plt.xlabel("Bulan")
plt.ylabel("Jumlah Rental Sepeda")
plt.xticks(fontsize=10, rotation=45)
plt.yticks(fontsize=10)
plt.legend(title="Tahun", loc="upper right")
plt.gca().xaxis.grid(False)
plt.grid(True)
st.pyplot(fig)

# === Perbandingan Penggunaan Sepeda Berdasarkan Jam ===
st.subheader("Perbandingan Jumlah Rental Sepeda Berdasarkan Jam")

fig, ax = plt.subplots(figsize=(10, 6))

bike_rental_hour = pd.read_csv("data/bike_hour.csv")
main_hour = bike_rental_hour[(bike_rental_hour["dteday"] >= str(start_date)) & 
                (bike_rental_hour["dteday"] <= str(end_date))]

sns.barplot(
    x="hr", 
    y="cnt",
    data=main_hour,
    hue="yr",
    palette="bright",
    ax=ax
)

ax.set_xlabel("Jam")
ax.set_ylabel("Jumlah Rental Sepeda")
plt.legend(title="Tahun")
plt.tight_layout()
st.pyplot(fig)

# === VISUALIASI Perbandingan Jumlah Rental Bike Berdasarkan Holiday dan Working Day ===
st.subheader("Perbandingan Jumlah Rental Sepeda Berdasarkan Hari Libur dan Hari Kerja")
holiday = main_df.groupby(by=["holiday"]).agg({
    "cnt": "sum"
})

working_day = main_df.groupby(by=["workingday"]).agg({
    "cnt": "sum"
})

colors_df = ['#4287f5', '#becee6']

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 10))
ax[0].pie(holiday["cnt"], labels=holiday.index, shadow=False, startangle=90, autopct="%1.1f%%", colors=colors_df)

ax[1].pie(working_day["cnt"], labels=working_day.index, autopct="%1.1f%%", shadow=False, startangle=90, colors=colors_df)

plt.tight_layout()

st.pyplot(fig)

# === Pola Penggunaan Sepeda pada Hari Kerja dan Hari Libur ===
fig, ax = plt.subplots(figsize=(10, 5))

# Visualisasi perbandingan penggunaan sepeda pada hari kerja dan hari libur
sns.barplot(
    x="workingday", 
    y="cnt",
    data=main_df,
    hue="yr",
    palette="bright",
    ax=ax
)

ax.set_xlabel("Hari Kerja")
ax.set_ylabel("Jumlah Rental Sepeda")
plt.legend(title="Tahun")
plt.xticks(ticks=[0, 1], labels=["Hari Libur", "Hari Kerja"])
plt.tight_layout()
st.pyplot(fig)

# === VISUALISASI Jumlah Rental Sepeda Berdasarkan Kondisi Cuaca dan Musim ===
st.subheader("Perbandingan Jumlah Rental Sepeda Berdasarkan Kondisi Cuaca dan Musim")
fig = plt.figure(figsize=(12, 6))

sns.barplot(
    y="cnt", 
    x="season",
    data=main_df.groupby(by=["season", "weathersit"]).agg({
    "cnt": "mean",}),
    hue="weathersit",
    palette="bright"
)
plt.ylabel("Jumlah Rental Sepeda")
plt.xlabel("Musim")
plt.tick_params(axis="both", labelsize=12)
plt.legend(title = "Kondisi Cuaca")
plt.tight_layout()
st.pyplot(fig)

# === VISUALISASI Perbandingan Rental Bike Berdasarkan Temperatur, Kelembaban, dan Windspeed ===
st.subheader("Perbandingan Jumlah Rental Bike Berdasarkan Faktor Lingkungan")
fig, axes = plt.subplots(1, 3, figsize=(21, 9))

# Visualisasi perbandingan rental bike berdasarkan temperatur
sns.regplot(
    x="temp", 
    y="cnt",
    data=main_df,
    color='blue',
    ax=axes[0]
)
axes[0].set_title("Jumlah Rental Bike Berdasarkan Temperatur")
axes[0].set_xlabel("Temperatur")
axes[0].set_ylabel("Jumlah Rental Bike")

# Visualisasi perbandingan rental bike berdasarkan kelembaban
sns.regplot(
    x="hum", 
    y="cnt",
    data=main_df,
    color='green',
    ax=axes[1]
)
axes[1].set_title("Jumlah Rental Bike Berdasarkan Kelembaban")
axes[1].set_xlabel("Kelembaban")
axes[1].set_ylabel("Jumlah Rental Bike")

# Visualisasi perbandingan rental bike berdasarkan windspeed
sns.regplot(
    x="windspeed", 
    y="cnt",
    data=main_df,
    color='orange',
    ax=axes[2]
)
axes[2].set_title("Jumlah Rental Bike Berdasarkan Windspeed")
axes[2].set_xlabel("Kecepatan Angin")
axes[2].set_ylabel("Jumlah Rental Bike")

plt.tight_layout()
st.pyplot(fig)

Year = datetime.date.today().year
Name = "[Albert Nathaniel](http://linkedin.com/in/albertnathaniel)"
Copyright = 'Copyright © ' + str(Year) + ' | ' + Name
st.caption(Copyright)