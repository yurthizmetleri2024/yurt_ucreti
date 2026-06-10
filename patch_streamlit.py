import os
import streamlit as st
import base64
import json

# Streamlit'in Render içindeki kök dosyasını buluyoruz
st_path = os.path.dirname(st.__file__)
index_path = os.path.join(st_path, "static", "index.html")

with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# 1. Başlığı kökten değiştiriyoruz
html_content = html_content.replace("<title>Streamlit</title>", "<title>Yurt Ücreti Hesaplama</title>")

# 2. Logoyu ve Android'in zorunlu tuttuğu "Manifest" (Kimlik) dosyasını oluşturuyoruz
try:
    with open("logo.png", "rb") as img_file:
        logo_b64 = base64.b64encode(img_file.read()).decode()
        logo_veri_yolu = f"data:image/png;base64,{logo_b64}"
    
    # Telefonu "Ben bir uygulamayım ve tam ekran çalışırım" diye ikna eden kimlik kartı
    manifest_ayarlari = {
        "name": "Yurt Ücreti Hesaplama",
        "short_name": "Yurt Ücreti",
        "start_url": "./",
        "display": "standalone",  # İŞTE SİHRİ YAPAN KISIM BU (Tarayıcı çubuğunu yok eder)
        "background_color": "#ffffff",
        "theme_color": "#ffffff",
        "icons": [
            {"src": logo_veri_yolu, "sizes": "192x192", "type": "image/png"},
            {"src": logo_veri_yolu, "sizes": "512x512", "type": "image/png"}
        ]
    }
    
    # Bu kimliği telefonun okuyabileceği şifreli (base64) bir koda çeviriyoruz
    manifest_json = json.dumps(manifest_ayarlari)
    manifest_b64 = base64.b64encode(manifest_json.encode('utf-8')).decode()
    manifest_veri_yolu = f"data:application/manifest+json;base64,{manifest_b64}"
    
    # Tüm bu etiketleri HTML'in beynine (<head>) kazıyoruz
    pwa_kodlari = f"""
    <link rel="manifest" href="{manifest_veri_yolu}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Yurt Ücreti">
    <link rel="apple-touch-icon" href="{logo_veri_yolu}">
    <link rel="icon" type="image/png" href="{logo_veri_yolu}">
    """
    
    # Kodları dosyaya yerleştiriyoruz
    if "</head>" in html_content and "apple-mobile-web-app-capable" not in html_content:
        html_content = html_content.replace("</head>", pwa_kodlari + "</head>")
        
except Exception as e:
    print("Kurulum sırasında küçük bir hata oluştu:", e)

# Değişiklikleri kaydedip sunucuyu ayağa kaldırıyoruz
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_content)