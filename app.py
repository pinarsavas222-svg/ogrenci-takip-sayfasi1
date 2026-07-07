import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
# Google Bağlantısı (Sadece bir kere tanımlanır)
conn = st.connection("gsheets", type=GSheetsConnection)
from datetime import date, datetime

# 1. Sayfa Tasarımı ve Başlık Ayarları
st.set_page_config(page_title="Pınar Öğretmen Koçluk Paneli", page_icon="📐", layout="wide")

# 2. Uygulama Hafızası (Session State) Kurulumu
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state: # "ogretmen" veya "ogrenci"
    st.session_state.user_type = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Verileri Google'dan çekiyoruz
df_odevler = conn.read(worksheet="Odevler")
df_denemeler = conn.read(worksheet="Denemeler")

# 3. Giriş Bilgileri Tanımlama
USERS = {
    "pinar": {"şifre": "hoca123", "tip": "ogretmen", "isim": "Pınar Öğretmen"},
    "ahmet": {"şifre": "1234", "tip": "ogrenci", "isim": "Ahmet Yılmaz"},
    "zeynep": {"şifre": "5678", "tip": "ogrenci", "isim": "Zeynep Kaya"}
}

# LGS 2027 Geri Sayım Sayacı (Haziran 2027 varsayılan)
def geri_sayim():
    sinav_tarihi = datetime(2027, 6, 5) # 2027 LGS Tahmini Tarih
    bugun = datetime.now()
    kalan_zaman = sinav_tarihi - bugun
    if kalan_zaman.days > 0:
        st.metric(label="⏳ 2027 LGS Sınavına Kalan Gün", value=f"{kalan_zaman.days} Gün")
    else:
        st.metric(label="⏳ 2027 LGS Sınavı", value="Sınav Günü Geldiler!")

# ==========================================
# GİRİŞ EKRANI
# ==========================================
if not st.session_state.logged_in:
    st.title("📐 Pınar Öğretmen - Eğitim Koçluğu & Matematik Paneli")
    st.subheader("Giriş Yaparak Sisteminize Ulaşın")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("Kullanıcı Adı (pinar / ahmet / zeynep)").strip().lower()
        password = st.text_input("Şifre (hoca123 / 1234 / 5678)", type="password")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if username in USERS and USERS[username]["şifre"] == password:
                st.session_state.logged_in = True
                st.session_state.user_type = USERS[username]["tip"]
                st.session_state.current_user = USERS[username]["isim"]
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
    with col2:
        st.info("💡 **Denemek İçin Giriş Bilgileri:**\n\n* **Öğretmen:** pinar / hoca123\n* **Öğrenci 1:** ahmet / 1234\n* **Öğrenci 2:** zeynep / 5678")

# ==========================================
# ÖĞRETMEN PANELİ
# ==========================================
elif st.session_state.user_type == "ogretmen":
    st.sidebar.title("🛠️ Öğretmen Menüsü")
    st.sidebar.write(f"Hoş geldiniz, **{st.session_state.current_user}** 👋")
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.title("👩‍🏫 Yönetim ve Eğitim Koçu Paneli")
    st.write("Tüm öğrencilerinizin durumunu buradan canlı olarak izleyebilir ve ödev atayabilirsiniz.")
    
    # Öğrenci Seçimi
    secilen_ogrenci = st.selectbox("Durumunu İncelemek İstediğiniz Öğrenci:", list(st.session_state.student_data.keys()))
    
    data = st.session_state.student_data[secilen_ogrenci]
    
    o_tab1, o_tab2, o_tab3 = st.tabs(["➕ Yeni Ödev Ver", "📊 Sınavlar & Konu Analizleri", "📚 Yanlış Defteri İncele"])
    
    with o_tab1:
        st.subheader(f"📝 {secilen_ogrenci} İçin Ödev Yönetimi")
        
        # Yeni Ödev Ekleme Formu
        with st.form("yeni_odev_formu"):
            yeni_odev_tanim = st.text_input("Ödev Açıklaması (Örn: Köklü Sayılar MEB Esaslı Sorular sayfa 40-50)")
            if st.form_submit_button("Ödevi Öğrenciye Ata"):
                if yeni_odev_tanim:
                    yeni_id = len(data["homeworks"]) + 1
                    data["homeworks"].append({"id": yeni_id, "tanim": yeni_odev_tanim, "tamamlandi": False})
                    st.success(f"Ödev {secilen_ogrenci} paneline başarıyla eklendi!")
                    st.rerun()
        
        # Mevcut Ödevlerin Durumu
        st.write("**Mevcut Ödev Durumları:**")
        for o in data["homeworks"]:
            durum = "✅ Tamamlandı" if o["tamamlandi"] else "⏳ Yapılmadı"
            st.write(f"- {o['tanim']} -> **{durum}**")
            
    with o_tab2:
        st.subheader(f"📊 {secilen_ogrenci} Gelişim Grafikleri")
        if data["exams"]:
            df_o = pd.DataFrame(data["exams"])
            st.line_chart(df_o.set_index("Deneme Adı")[["Net"]])
            st.dataframe(df_o)
        else:
            st.info("Öğrenci henüz deneme sınavı girmedi.")
            
        st.subheader("📐 Matematik Konu İlerleme Yüzdeleri")
        for konu, yuzde in data["topics"].items():
            st.write(f"{konu}:")
            st.progress(yuzde / 100.0)
            
    with o_tab3:
        st.subheader(f"📚 {secilen_ogrenci} Tarafından Yüklenen Hatalı Sorular")
        if data["mistakes"]:
            for i, m in enumerate(data["mistakes"]):
                with st.expander(f"Soru {i+1} - {m['tarih']}"):
                    st.image(m['foto'], use_container_width=True)
                    st.write(f"**Hata Nedeni:** {m['neden']}")
                    st.write(f"**Doğru Çözüm Notu:** {m['cozum']}")
        else:
            st.info("Öğrenci henüz yanlış defterine soru yüklemedi.")

# ==========================================
# ÖĞRENCİ PANELİ
# ==========================================
elif st.session_state.user_type == "ogrenci":
    ogrenci_ismi = st.session_state.current_user
    data = st.session_state.student_data[ogrenci_ismi]
    
    st.sidebar.title("👤 Öğrenci Profili")
    st.sidebar.write(f"Hoş geldin, **{ogrenci_ismi}** ✨")
    st.sidebar.caption("Danışman: Pınar Öğretmen")
    
    # Sayacı Sidebar'a koyalım
    with st.sidebar:
        st.markdown("---")
        geri_sayim()
        st.markdown("---")
        
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.title(f"🚀 Başarı Takip Panelin")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Ödevlerim", "📚 Yanlış Defterim", "📊 Deneme Takibim", "📐 Matematik Konu Analizi"])
    
    # TAB 1: ÖDEVLER
    with tab1:
        st.header("Yapılacak Ödevlerin")
        st.caption("Ödevini bitirdiğinde kutucuğu işaretle, Pınar Öğretmenine anında raporlansın.")
        
        for index, odev in enumerate(data["homeworks"]):
            key = f"odev_{ogrenci_ismi}_{odev['id']}"
            checked = st.checkbox(odev['tanim'], value=odev['tamamlandi'], key=key)
            
            if checked and not odev['tamamlandi']:
                data["homeworks"][index]['tamamlandi'] = True
                st.toast(f"📧 PINAR ÖĞRETMENE BİLDİRİM: {ogrenci_ismi} '{odev['tanim']}' ödevini bitirdi!", icon="🚀")
                st.rerun()
            elif not checked and odev['tamamlandi']:
                data["homeworks"][index]['tamamlandi'] = False
                st.rerun()

    # TAB 2: YANLIŞ DEFTERİ
    with tab2:
        st.header("🧠 Dijital Yanlış Defterim")
        with st.form("ogrenci_yanlis_formu", clear_on_submit=True):
            uploaded_file = st.file_uploader("Sorunun Fotoğrafını Yükle", type=["jpg", "png", "jpeg"])
            hata_nedeni = st.text_area("Bu soruda neden hata yaptın?")
            dogru_cozum = st.text_area("Sorunun Doğru Çözüm Mantığı:")
            if st.form_submit_button("Yanlış Defterine Kaydet"):
                if uploaded_file and hata_nedeni and dogru_cozum:
                    data["mistakes"].append({
                        "foto": uploaded_file.read(),
                        "neden": hata_nedeni,
                        "cozum": dogru_cozum,
                        "tarih": date.today().strftime("%d.%m.%Y")
                    })
                    st.success("Soru başarıyla defterine eklendi!")
                    st.rerun()
                    
        if data["mistakes"]:
            for i, m in enumerate(reversed(data["mistakes"])):
                with st.expander(f"❌ Soru {len(data['mistakes']) - i}"):
                    st.image(m['foto'], use_container_width=True)
                    st.write(f"**Hata Nedeni:** {m['neden']}")
                    st.write(f"**Doğru Çözüm:** {m['cozum']}")

    # TAB 3: DENEME Sınavları
    with tab3:
        st.header("📊 Deneme Performansım")
        with st.form("ogrenci_deneme_formu", clear_on_submit=True):
            d_adi = st.text_input("Deneme Sınavı Adı (Örn: TÖDER LGS-1)")
            col1, col2 = st.columns(2)
            with col1: d = st.number_input("Matematik Doğru", min_value=0, max_value=20, step=1)
            with col2: y = st.number_input("Matematik Yanlış", min_value=0, max_value=20, step=1)
            if st.form_submit_button("Sonucu İşle") and d_adi:
                net = d - (y * 0.33) # LGS'de 3 yanlış 1 doğruyu götürür
                data["exams"].append({"Tarih": date.today().strftime("%Y-%m-%d"), "Deneme Adı": d_adi, "Doğru": d, "Yanlış": y, "Net": round(net, 2)})
                st.success("Deneme sonucu eklendi!")
                st.rerun()
                
        if data["exams"]:
            df = pd.DataFrame(data["exams"])
            st.line_chart(df.set_index("Deneme Adı")[["Net"]])
            st.dataframe(df)

    # TAB 4: MATEMATİK KONU ANALİZİ
    with tab4:
        st.header("📐 LGS Matematik Konu Yetkinlik Durumun")
        st.write("Pınar Öğretmeninin senin için belirlediği konu hakimiyet yüzdeleri:")
        
        # Öğrencinin konuları görmesi ve kendisinin de güncelleyebilmesi için
        for konu, yuzde in data["topics"].items():
            st.write(f"**{konu}** (Hakimiyet: %{yuzde})")
            st.progress(yuzde / 100.0)
