import streamlit as st
import pandas as pd
import numpy as np

# Sayfa yapılandırması
st.set_page_config(page_title="Yurt Ücret Hesaplama ve Gelir Analizi", layout="wide")

# Başlık
st.title("📊 Yurt Ücreti Senaryo ve Gelir Analiz Paneli")
st.markdown("TÜFE, ÜFE veya Manuel artış modelleri simülasyonu.")

# --- 1. VERİ HAZIRLAMA ---
@st.cache_data
def veri_hazirla():
    # Sıralama: KIBRIS en sonda yer alıyor
    data = {
        'Yurt Tipi': ['Tip 1', 'Tip 2', 'Tip 3', 'Tip 4', 'Tip 5', 'KIBRIS'],
        'Mevcut Ücret': [725, 850, 1000, 1100, 1200, 1700],
        'Öğrenci Sayısı': [50000, 75000, 120000, 90000, 60000, 30000]
    }
    return pd.DataFrame(data)

df = veri_hazirla()

# --- 2. YAN MENÜ (SENARYO SEÇİMİ) ---
st.sidebar.header("⚙️ Hesaplama Modeli")

model_secimi = st.sidebar.radio(
    "Artış Kriterini Seçiniz:",
    ("TÜFE Bazlı", "ÜFE Bazlı", "Manuel Oran Girişi")
)

# Seçime göre dinamik girdi kutusu
if model_secimi == "TÜFE Bazlı":
    oran = st.sidebar.slider("Yıllık TÜFE Oranı (%)", 0.0, 120.0, 32.61, 0.5)
elif model_secimi == "ÜFE Bazlı":
    oran = st.sidebar.slider("Yıllık ÜFE Oranı (%)", 0.0, 120.0, 28.93, 0.5)
else:
    oran = st.sidebar.number_input("Özel Artış Oranı (%)", 0.0, 200.0, 50.0, 1.0)

# --- 3. HESAPLAMA MOTORU ---
df['Yeni Ücret'] = df['Mevcut Ücret'] * (1 + (oran / 100))
df['Ücret Farkı (Kişi Başı)'] = df['Yeni Ücret'] - df['Mevcut Ücret']

df['Eski Aylık Toplam'] = df['Mevcut Ücret'] * df['Öğrenci Sayısı']
df['Yeni Aylık Toplam'] = df['Yeni Ücret'] * df['Öğrenci Sayısı']
df['Gelir Farkı (Aylık)'] = df['Yeni Aylık Toplam'] - df['Eski Aylık Toplam']

# --- 4. ÜST METRİKLER (ANLIK DEĞİŞEN) ---
eski_toplam_gelir = df['Eski Aylık Toplam'].sum()
yeni_toplam_gelir = df['Yeni Aylık Toplam'].sum()
fark_toplam = df['Gelir Farkı (Aylık)'].sum()
toplam_ogrenci = df['Öğrenci Sayısı'].sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Toplam Öğrenci", f"{toplam_ogrenci:,}".replace(",", "."))
c2.metric("Uygulanan Zam", f"% {oran:.2f}")
c3.metric("Mevcut Aylık Gelir", f"{eski_toplam_gelir:,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
c4.metric("Yeni Aylık Gelir", f"{yeni_toplam_gelir:,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
c5.metric("Aylık Ek Gelir Hacmi", f"{fark_toplam:,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

st.divider()

# --- 5. TABLO VE GRAFİK BÖLÜMÜ ---
sol_col, sag_col = st.columns([1.3, 1])

with sol_col:
    st.subheader("📋 Detaylı Hesaplama Matrisi")
    
    gosterilecek_df = df[[
        'Yurt Tipi', 'Mevcut Ücret', 'Yeni Ücret', 
        'Ücret Farkı (Kişi Başı)', 'Öğrenci Sayısı', 'Gelir Farkı (Aylık)'
    ]]
    
    st.dataframe(
        gosterilecek_df.style.format({
            'Mevcut Ücret': '{:,.2f} TL',
            'Yeni Ücret': '{:,.2f} TL',
            'Ücret Farkı (Kişi Başı)': '{:,.2f} TL',
            'Öğrenci Sayısı': '{:,}',
            'Gelir Farkı (Aylık)': '{:,.2f} TL'
        }, thousands='.', decimal=','),
        use_container_width=True,
        hide_index=True
    )

with sag_col:
    st.subheader("📈 Gelir Karşılaştırması")
    st.caption("Mevcut vs Yeni Gelir (Aylık)")
    
    # Orijinal sıra korunarak KIBRIS'ın sonda çıkması sağlandı
    st.bar_chart(
        df, 
        x='Yurt Tipi', 
        y=['Eski Aylık Toplam', 'Yeni Aylık Toplam'], 
        use_container_width=True
    )

st.info("💡 Not: Yukarıdaki veriler, soldan seçtiğiniz modele göre anlık olarak yeniden hesaplanmaktadır.")