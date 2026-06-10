import os
import streamlit as st
import base64

# Streamlit'in Render içindeki ana index.html dosyasının yolunu buluyoruz
st_path = os.path.dirname(st.__file__)
index_path = os.path.join(st_path, "static", "index.html")

with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# 1. Başlığı kökten değiştiriyoruz (Chrome artık ilk saniyede bunu okuyacak)
html_content = html_content.replace("<title>Streamlit</title>", "<title>Yurt Ücreti Hesaplama</title>")

# 2. Logoyu telefonun doğrudan tanıyabilmesi için Base64 formatına çevirip HTML kafasına gömüyoruz
try:
    with open("logo.png", "rb") as img_file:
        logo_b64 = base64.b64encode(img_file.read()).decode()
    
    pwa_meta = f"""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="Yurt Ücreti Hesaplama">
    <link rel="icon" type="image/png" href="data:image/png;base64,{logo_b64}">
    <link rel="apple-touch-icon" href="data:image/png;base64,{logo_b64}">
    """
    
    # Kodları </head> etiketinin hemen öncesine enjekte ediyoruz
    if "</head>" in html_content and "mobile-web-app-capable" not in html_content:
        html_content = html_content.replace("</head>", pwa_meta + "</head>")
        print("Logo ve PWA ayarları kök koda başarıyla gömüldü.")
except Exception as e:
    print("Logo kök koda gömülürken hata oluştu:", e)

# Değişiklikleri kaydediyoruz
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_content)