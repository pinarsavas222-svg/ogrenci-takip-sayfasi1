import streamlit as st
import pandas as pd
from datetime import date

# 1. Sayfa Tasarımı ve Başlık Ayarları
st.set_page_config(page_title="Öğrenci Takip Sistemi", page_icon="🎓", layout="centered")

# 2. Uygulama Hafızası (Session State) Kurulumu
# Sayfa yenilendiğinde veya sekmeler arası geçişte verilerin kaybolmaması için geçici hafıza oluşturuyoruz
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "homeworks" not in st.session_state:
    st.session_state.homeworks = [
        {"id": 1, "tanim": "Matematik - Yeni Nesil Üslü Sayılar Test 1", "tamamlandi": False},
        {"id": 2, "tanim": "Geometri - Üçgende Açılar Fasikülü", "tamamlandi": False},
        {"id": 3, "tanim": "LGS Deneme - 2 Eksik Analizlerinin Yapılması", "tamamlandi": False}
    ]
if "mistakes" not in st.session_state:
    st.session_state.mistakes = []
if "exams" not in st.session_state:
    st.session_state.exams = []

# 3. Mail Gönderme Simülasyonu
def mail_gonder(odev_adi):
    # Gerçek sistemde buraya SMTP mail kodları entegre edilir.
    # Canlı testlerde sistemin çalıştığını görmek için ekrana dinamik bir e-posta uyarısı fırlatıyoruz.
    st.toast(f"📧 VELİYE BİLGİLENDİRME: 'İşaretlenen Ödev: {odev_adi}' başarıyla tamamlandı!", icon="🚀")

# ==========================================
# GİRİŞ EKRANI
# ==========================================
if not st.session_state.logged_in:
    st.title("🎓 Öğrenci Giriş Paneli")
    st.write("Lütfen öğretmeninizin size verdiği bilgilerle giriş yapın.")
    
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap", use_container_width=True):
        # Örnek giriş bilgileri (İleride bir veri tabanına bağlanabilir)
        if username == "ogrenci" and password == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre! (Denemek için ogrenci / 1234 yazın)")

# ==========================================
# ANA UYGULAMA PANELİ (Giriş Yapıldıysa)
# ==========================================
else:
    # Sol Menü (Sidebar)
    st.sidebar.title("👤 Öğrenci Profili")
    st.sidebar.write("Hoş geldin, *Başarılı Öğrenci* 👋")
    st.sidebar.info("Danışman: Pınar Öğretmen")
    
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.title("🚀 Öğrenci Gelişim ve Takip Paneli")
    st.write("Ödevlerini tamamla, hatalarını kaydet ve gelişimini grafiklerle izle.")
    
    # Sekmeler (Tabs) Oluşturma
    tab1, tab2, tab3 = st.tabs(["📝 Ödevlerim", "📚 Yanlış Defterim", "📊 Deneme Takibi"])
    
    # ------------------------------------------
    # TAB 1: ÖDEVLERİM VE MAİL SİSTEMİ
    # ------------------------------------------
    with tab1:
        st.header("Yapılacak Ödevler")
        st.caption("Ödevini bitirdiğinde kutucuğu işaretle, veline anında e-posta gitsin.")
        
        for index, odev in enumerate(st.session_state.homeworks):
            key = f"odev_{odev['id']}"
            
            # Öğrenci kutucuğu işaretliyor mu kontrolü
            checked = st.checkbox(odev['tanim'], value=odev['tamamlandi'], key=key)
            
            # Durum değişikliği yönetimi
            if checked and not odev['tamamlandi']:
                st.session_state.homeworks[index]['tamamlandi'] = True
                mail_gonder(odev['tanim'])
                st.rerun()
            elif not checked and odev['tamamlandi']:
                st.session_state.homeworks[index]['tamamlandi'] = False
                st.rerun()

    # ------------------------------------------
    # TAB 2: YANLIŞ DEFTERİ (FOTOĞRAF + NOT)
    # ------------------------------------------
    with tab2:
        st.header("🧠 Dijital Yanlış Defteri")
        st.write("Seni sınavda öne geçirecek olan yapamadığın sorulardır. Buraya yükle!")
        
        with st.form("yanlis_formu", clear_on_submit=True):
            uploaded_file = st.file_uploader("Sorunun Fotoğrafını Çek veya Yükle", type=["jpg", "png", "jpeg"])
            hata_nedeni = st.text_area("Bu soruda nerede hata yaptın? (Örn: Soru kökünü yanlış okudum, formülü unuttum...)")
            dogru_cozum = st.text_area("Sorunun Doğru Çözüm Mantığı:")
            
            submit_button = st.form_submit_button("Yanlış Defterine Kaydet", use_container_width=True)
            
            if submit_button:
                if uploaded_file and hata_nedeni and dogru_cozum:
                    # Yeni hatayı hafızaya ekleme
                    yeni_hata = {
                        "foto": uploaded_file.read(),
                        "neden": hata_nedeni,
                        "cozum": dogru_cozum,
                        "tarih": date.today().strftime("%d.%m.%Y")
                    }
                    st.session_state.mistakes.append(yeni_hata)
                    st.success("Harika! Soru başarıyla yanlış defterine eklendi.")
                else:
                    st.warning("Lütfen fotoğraf yükleyin ve metin alanlarını doldurun.")
                    
        # Kaydedilen Soruları Listeleme
        if st.session_state.mistakes:
            st.subheader("📚 Kaydedilen Hatalı Sorularım")
            for i, m in enumerate(reversed(st.session_state.mistakes)):
                with st.expander(f"❌ Soru {len(st.session_state.mistakes) - i} - Tarih: {m['tarih']}"):
                    st.image(m['foto'], caption="Öğrencinin Yüklediği Soru", use_container_width=True)
                    st.markdown(f"*🧐 Hata Nedeni:* {m['neden']}")
                    st.markdown(f"*💡 Doğru Çözüm Notu:* {m['cozum']}")

    # ------------------------------------------
    # TAB 3: DENEME SINAVI GRAFİK TAKİBİ
    # ------------------------------------------
    with tab3:
        st.header("📊 Deneme Sınavı Performansı")
        
        # Veri Giriş Formu
        with st.form("deneme_formu", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                deneme_tarih = st.date_input("Sınav Tarihi", date.today())
                deneme_adi = st.text_input("Deneme Sınavı Adı (Örn: Özdebir LGS-1)")
            with col2:
                dogru = st.number_input("Doğru Sayısı", min_value=0, max_value=100, step=1)
                yanlis = st.number_input("Yanlış Sayısı", min_value=0, max_value=100, step=1)
                
            deneme_submit = st.form_submit_button("Deneme Sonucunu İşle", use_container_width=True)
            
            if deneme_submit and deneme_adi:
                # Klasik net hesabı (3 yanlış 1 doğruyu götürür veya isteğe göre 4 yanlış)
                net = dogru - (yanlis * 0.25) 
                yeni_deneme = {
                    "Tarih": deneme_tarih.strftime("%Y-%m-%d"),
                    "Deneme Adı": deneme_adi,
                    "Doğru": dogru,
                    "Yanlış": yanlis,
                    "Net": net
                }
                st.session_state.exams.append(yeni_deneme)
                st.success("Deneme sonucu başarıyla listeye eklendi!")
                st.rerun()

        # Grafik ve Tablo Alanı
        if st.session_state.exams:
            df = pd.DataFrame(st.session_state.exams)
            
            st.subheader("📈 Net Değişim Grafiğin")
            # Çizgi grafiği için netleri index yapıyoruz
            chart_data = df.set_index("Deneme Adı")[["Net"]]
            st.line_chart(chart_data)
            
            st.subheader("📋 Tüm Sınav Sonuçları")
            st.dataframe(df, use_container_width=True)