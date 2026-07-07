import streamlit as st
import pandas as pd
from datetime import date, datetime

# 1. Sayfa Tasarımı ve Başlık Ayarları
st.set_page_config(page_title="Pınar Öğretmen Koçluk Paneli", page_icon="📐", layout="wide")

# 2. Uygulama Hafızası (Session State) Kurulumu
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state: 
    st.session_state.user_type = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Örnek Öğrenci Veritabanı
if "student_data" not in st.session_state:
    st.session_state.student_data = {
        "Ahmet Yılmaz": {
            "homeworks": [
                {"id": 1, "tanim": "Matematik - Çarpanlar ve Katlar Test 1 & 2", "tamamlandi": False},
                {"id": 2, "tanim": "LGS Deneme Analizi Yapılacak", "tamamlandi": True}
            ],
            "mistakes": [],
            "exams": [{"Tarih": "2026-06-15", "Deneme Adı": "Özdebir LGS-1", "Doğru": 16, "Yanlış": 4, "Net": 15.0}],
            "topics": {"Çarpanlar ve Katlar": 40, "Üslü İfadeler": 10, "Köklü İfadeler": 0}
        },
        "Zeynep Kaya": {
            "homeworks": [
                {"id": 3, "tanim": "Matematik - Üslü Sayılar Yeni Nesil Soru Çözümü", "tamamlandi": False}
            ],
            "mistakes": [],
            "exams": [{"Tarih": "2026-06-16", "Deneme Adı": "Özdebir LGS-1", "Doğru": 18, "Yanlış": 2, "Net": 17.5}],
            "topics": {"Çarpanlar ve Katlar": 80, "Üslü İfadeler": 60, "Köklü İfadeler": 20}
        }
    }

# 3. Giriş Bilgileri
USERS = {
    "pinar": {"şifre": "hoca123", "tip": "ogretmen", "isim": "Pınar Öğretmen"},
    "ahmet": {"şifre": "1234", "tip": "ogrenci", "isim": "Ahmet Yılmaz"},
    "zeynep": {"şifre": "5678", "tip": "ogrenci", "isim": "Zeynep Kaya"}
}

def geri_sayim():
    sinav_tarihi = datetime(2027, 6, 5)
    bugun = datetime.now()
    kalan_zaman = sinav_tarihi - bugun
    if kalan_zaman.days > 0:
        st.metric(label="⏳ 2027 LGS'ye Kalan Gün", value=f"{kalan_zaman.days} Gün")

# Giriş Ekranı
if not st.session_state.logged_in:
    st.title("📐 Pınar Öğretmen - Eğitim Koçluğu Paneli")
    username = st.text_input("Kullanıcı Adı").strip().lower()
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if username in USERS and USERS[username]["şifre"] == password:
            st.session_state.logged_in = True
            st.session_state.user_type = USERS[username]["tip"]
            st.session_state.current_user = USERS[username]["isim"]
            st.rerun()
        else:
            st.error("Hatalı giriş!")

# Uygulama Panelleri
elif st.session_state.user_type == "ogretmen":
    st.sidebar.title("Öğretmen Menüsü")
    if st.sidebar.button("Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("👩‍🏫 Yönetim Paneli")
    secilen_ogrenci = st.selectbox("Öğrenci Seç:", list(st.session_state.student_data.keys()))
    data = st.session_state.student_data[secilen_ogrenci]
    
    tab1, tab2 = st.tabs(["Ödevler", "Grafikler"])
    with tab1:
        for o in data["homeworks"]:
            st.write(f"- {o['tanim']} ({'✅' if o['tamamlandi'] else '⏳'})")
    with tab2:
        if data["exams"]:
            st.line_chart(pd.DataFrame(data["exams"]).set_index("Deneme Adı")[["Net"]])

elif st.session_state.user_type == "ogrenci":
    data = st.session_state.student_data[st.session_state.current_user]
    st.sidebar.title("Öğrenci Paneli")
    if st.sidebar.button("Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title(f"Merhaba {st.session_state.current_user}")
    geri_sayim()
