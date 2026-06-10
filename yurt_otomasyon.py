import streamlit as st
import pandas as pd
from PIL import Image

# --- 1. SAYFA VE MOBİL APP AYARLARI ---
# Klasörde logo.png varsa kullanır, yoksa standart bina ikonu koyar
try:
    uygulama_ikonu = Image.open("logo.png")
    st.set_page_config(page_title="KYK Analiz", page_icon=uygulama_ikonu, layout="centered", initial_sidebar_state="collapsed")
except:
    st.set_page_config(page_title="KYK Analiz", page_icon="🏢", layout="centered", initial_sidebar_state="collapsed")

# Streamlit izlerini gizleyen ve sekmeleri ekrana yayan CSS
gizleme_stili = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container { padding-top: 1rem; padding-bottom: 0rem; }
            div[data-testid="stTabs"] button { flex: 1; font-size: 16px; font-weight: bold; }
            </style>
            """
st.markdown(gizleme_stili, unsafe_allow_html=True)

st.title("📱 Yurt Yönetim Paneli")

# --- 2. VERİ HAZIRLAMA ---
@st.cache_data
def veri_hazirla():
    data = {
        'Yurt Tipi': ['Tip 1', 'Tip 2', 'Tip 3', 'Tip 4', 'Tip 5', 'KIBRIS'],
        'Mevcut Ücret': [725, 850, 1000, 1100, 1200, 1700],
        'Öğrenci Sayısı': [50000, 75000, 120000, 90000, 60000, 30000]
    }
    return pd.DataFrame(data)

df = veri_hazirla()

# --- 3. APP MENÜSÜ (İKİ SEKME) ---
tab_ucret, tab_gelir = st.tabs(["💸 Ücretler", "📊 Gelirler"])

# --- 4. ÜCRETLER VE SENARYO MODÜLÜ ---
with tab_ucret:
    st.subheader("Artış Modelini Belirle")
    model_secimi = st.radio(
        "Hesaplama Kriteri:", 
        ("TÜFE Bazlı", "ÜFE Bazlı", "Manuel Oran"), 
        horizontal=True 
    )
    
    # Seçime göre dinamik oran belirleme
    if model_secimi == "TÜFE Bazlı":
        oran = st.slider("Yıllık TÜFE Oranı (%)", 0.0, 120.0, 32.61, 0.5)
    elif model_secimi == "ÜFE Bazlı":
        oran = st.slider("Yıllık ÜFE Oranı (%)", 0.0, 120.0, 28.93, 0.5)
    else:
        oran = st.number_input("Özel Artış Oranı (%)", 0.0, 200.0, 50.0, 1.0)

    # --- HESAPLAMA MOTORU (Oran belirlendikten hemen sonra çalışır) ---
    df['Yeni Ücret'] = df['Mevcut Ücret'] * (1 + (oran / 100))
    df['Ücret Farkı'] = df['Yeni Ücret'] - df['Mevcut Ücret']

    df['Eski Aylık Toplam'] = df['Mevcut Ücret'] * df['Öğrenci Sayısı']
    df['Yeni Aylık Toplam'] = df['Yeni Ücret'] * df['Öğrenci Sayısı']
    df['Aylık Ek Gelir'] = df['Yeni Aylık Toplam'] - df['Eski Aylık Toplam']
    
    st.divider() # Arayüzü rahatlatmak için ayırıcı çizgi
    
    # Oran ve Tablo Gösterimi
    st.metric("Uygulanan Zam Oranı", f"% {oran:.2f}")
    st.subheader("Öğrenci Başına Yansımalar")
    
    gosterilecek_ucret = df[['Yurt Tipi', 'Mevcut Ücret', 'Yeni Ücret', 'Ücret Farkı']]
    st.dataframe(
        gosterilecek_ucret.style.format({
            'Mevcut Ücret': '{:,.2f} TL',
            'Yeni Ücret': '{:,.2f} TL',
            'Ücret Farkı': '+ {:,.2f} TL'
        }, thousands='.', decimal=','),
        use_container_width=True,
        hide_index=True
    )

# --- 5. GELİRLER MODÜLÜ ---
with tab_gelir:
    st.subheader("Kurumsal Bütçe Analizi")
    
    # Toplam gelir kartları
    c1, c2 = st.columns(2)
    c1.metric("Mevcut Toplam", f"{df['Eski Aylık Toplam'].sum():,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("Yeni Toplam", f"{df['Yeni Aylık Toplam'].sum():,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
    
    # Net Artış Vurgusu
    st.metric("Aylık Net Gelir Artışı", f"+ {df['Aylık Ek Gelir'].sum():,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
    
    st.divider()
    st.caption("Mevcut vs Yeni Gelir Karşılaştırması")
    
    # Grafik (KIBRIS sırasını korur)
    st.bar_chart(
        df, 
        x='Yurt Tipi', 
        y=['Eski Aylık Toplam', 'Yeni Aylık Toplam'], 
        use_container_width=True
    )