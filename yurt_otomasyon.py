import streamlit as st
import pandas as pd
from PIL import Image
import base64

# --- 1. FONKSİYON: LOGOYU UYGULAMAYA GÖMME ---
def logoyu_base64_yap(dosya_yolu):
    try:
        with open(dosya_yolu, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# --- 2. SAYFA VE MOBİL APP AYARLARI ---
try:
    uygulama_ikonu = Image.open("logo.png")
    st.set_page_config(
        page_title="Yurt Ücreti Hesaplama", 
        page_icon=uygulama_ikonu, 
        layout="centered", 
        initial_sidebar_state="collapsed"
    )
    # Logoyu telefonların çekebileceği formata çeviriyoruz
    logo_b64 = logoyu_base64_yap("logo.png")
except Exception as e:
    st.set_page_config(
        page_title="Yurt Ücreti Hesaplama", 
        page_icon="🏢", 
        layout="centered", 
        initial_sidebar_state="collapsed"
    )
    logo_b64 = None

# --- 3. PWA (MOBİL UYGULAMA) ETİKETLERİ ---
# Telefonun tarayıcı çubuğunu gizlemesi ve logoyu ana ekrana çekmesi için
mobil_app_kodlari = f"""
<style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .block-container {{ padding-top: 1rem; padding-bottom: 0rem; }}
    div[data-testid="stTabs"] button {{ flex: 1; font-size: 16px; font-weight: bold; }}
</style>

<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="KYK Analiz">
"""

# Eğer logo başarıyla okunduysa, telefonun ana ekranı için logoyu HTML'e zorla ekle
if logo_b64:
    mobil_app_kodlari += f'<link rel="apple-touch-icon" href="data:image/png;base64,{logo_b64}">'

st.markdown(mobil_app_kodlari, unsafe_allow_html=True)

st.title("📱 Yurt Yönetim Paneli")

# --- 4. VERİ HAZIRLAMA ---
@st.cache_data
def veri_hazirla():
    data = {
        'Yurt Tipi': ['Tip 1', 'Tip 2', 'Tip 3', 'Tip 4', 'Tip 5', 'KIBRIS'],
        'Mevcut Ücret': [725, 850, 1000, 1100, 1200, 1700],
        'Öğrenci Sayısı': [77501, 167528, 200478, 195022, 342085, 7041]
    }
    return pd.DataFrame(data)

df = veri_hazirla()

# --- 5. APP MENÜSÜ (İKİ SEKME) ---
tab_ucret, tab_gelir = st.tabs(["💸 Ücretler", "📊 Gelirler"])

# --- 6. ÜCRETLER VE SENARYO MODÜLÜ ---
with tab_ucret:
    st.subheader("Artış Modelini Belirle")
    model_secimi = st.radio(
        "Hesaplama Kriteri:", 
        ("TÜFE Bazlı", "ÜFE Bazlı", "Manuel Oran"), 
        horizontal=True 
    )
    
    if model_secimi == "TÜFE Bazlı":
        oran = st.slider("Yıllık TÜFE Oranı (%)", 0.0, 120.0, 32.61, 0.5)
    elif model_secimi == "ÜFE Bazlı":
        oran = st.slider("Yıllık ÜFE Oranı (%)", 0.0, 120.0, 28.93, 0.5)
    else:
        oran = st.number_input("Özel Artış Oranı (%)", 0.0, 200.0, 50.0, 1.0)

    # --- HESAPLAMA MOTORU ---
    df['Yeni Ücret'] = df['Mevcut Ücret'] * (1 + (oran / 100))
    df['Ücret Farkı'] = df['Yeni Ücret'] - df['Mevcut Ücret']

    df['Eski Aylık Toplam'] = df['Mevcut Ücret'] * df['Öğrenci Sayısı']
    df['Yeni Aylık Toplam'] = df['Yeni Ücret'] * df['Öğrenci Sayısı']
    df['Aylık Ek Gelir'] = df['Yeni Aylık Toplam'] - df['Eski Aylık Toplam']
    
    st.divider() 
    
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

# --- 7. GELİRLER MODÜLÜ ---
with tab_gelir:
    st.subheader("Kurumsal Bütçe Analizi")
    
    c1, c2 = st.columns(2)
    c1.metric("Mevcut Toplam", f"{df['Eski Aylık Toplam'].sum():,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("Yeni Toplam", f"{df['Yeni Aylık Toplam'].sum():,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("Aylık Net Gelir Artışı", f"+ {df['Aylık Ek Gelir'].sum():,.0f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
    
    st.divider()
    st.caption("Mevcut vs Yeni Gelir Karşılaştırması")
    
    st.bar_chart(
        df, 
        x='Yurt Tipi', 
        y=['Eski Aylık Toplam', 'Yeni Aylık Toplam'], 
        use_container_width=True
    )