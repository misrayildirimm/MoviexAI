import streamlit as st

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🏠 Film Projesine Hoş Geldiniz!",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gelişmiş CSS stilleri
st.markdown("""
    <style>
    /* Genel Streamlit arka plan rengini tam siyaha ayarla */
    body {
        background-color: #000000;
        color: #e0e0e0;
    }
    .stApp {
        background-color: #000000;
    }

    /* Ana başlık stili - Gradyanlı ve sol hizalı */
    h1 {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: left;
        background: linear-gradient(45deg, #E6E6FA, #D8BFD8, #DA70D6, #BA55D3, #4B0082);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem; /* Başlık ile altındaki boşluğu azalt */
        animation: gradientShift 4s ease-in-out infinite;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        line-height: 1.2; /* Satır yüksekliğini ayarla */
        padding-top: 0;
        padding-bottom: 0;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Logo container'ı için sağa hizalama ve dikey ortalama */
    .logo-container {
        display: flex;
        justify-content: flex-end; /* Logoyu sağa hizala */
        align-items: center; /* Logoyu dikeyde ortala */
        height: 100%; /* Sütunun tüm yüksekliğini almasını sağla */
        width: 100%; /* İçeriği doldurmasını sağla */
        padding: 0 !important; /* İç boşluğu sıfırla */
        margin: 0 !important; /* Dış boşluğu sıfırla */
    }

    /* Sol taraftaki metin container'ı için ayarlar */
    .text-container {
        display: flex;
        flex-direction: column; /* İçeriği dikey sırala */
        justify-content: center; /* Dikeyde ortala (eğer yüksekliği yeterliyse) */
        height: 100%; /* Sütunun tüm yüksekliğini almasını sağla */
        padding: 0 !important; /* İç boşluğu sıfırla */
        margin: 0 !important; /* Dış boşluğu sıfırla */
    }

    /* Streamlit'in kendi sütun elementleri için agresif sıfırlama */
    div[data-testid="stVerticalBlock"] > div:first-child > div:first-child {
        padding: 0px !important;
    }
    div[data-testid="column"] {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin: 0rem !important;
    }
    /* Sağ sütundaki padding'i özel olarak ayarla - daha da sağa yaslamak için */
    div[data-testid="column"]:nth-child(2) { /* İkinci sütun (sağdaki) için */
        padding-left: 0rem !important; /* Sol boşluğu kaldır */
        padding-right: 0rem !important; /* Tam sağa yaslamak için sağ boşluğu da kaldır */
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0rem; /* Dikey bloklar arası boşluğu kaldır */
    }

    /* st.image componentinin etrafındaki div'i hedefle ve resmi sağa yasla */
    div.stImage {
        display: flex !important;
        justify-content: flex-end !important; /* Resmi sağa yasla */
        width: 100% !important; /* Kapsayıcının tüm genişliğini kullan */
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Genel metinler ve alt başlıklar */
    h2, h3, h4, h5, h6 {
        color: #e0e0e0;
        text-align: left;
        margin-bottom: 0.8rem;
        margin-top: 0.8rem; /* Metinler için üst boşluğu azalt */
    }
    p {
        color: #d0d0d0;
        line-height: 1.6;
        text-align: left;
        max-width: 800px;
        margin-bottom: 0.5rem; /* Paragraflar arası boşluğu azalt */
    }

    /* Welcome section */
    .welcome-section {
        margin-top: 2rem; /* Başlık ile yazı arasına boşluk ekledik */
        margin-bottom: 0rem;
    }
    .welcome-section p {
        font-size: 1.15rem;
        color: #d0d0d0;
        margin-bottom: 0.5rem;
        max-width: 700px;
        text-align: left;
    }
    .welcome-section p b {
        color: #ffeaa7;
    }

    /* Navigation question section */
    .navigation-question {
        margin-top: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .navigation-question h3 {
        font-size: 2.2rem;
        color: #e0e0e0;
        margin-top: 1rem;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        text-align: center;
    }

    /* Buton container - tam ortada, eşit genişlikte */
    .button-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 25px;
        margin: 2rem auto;
        max-width: 1200px;
        flex-wrap: wrap;
    }

    /* Streamlit butonlarını özelleştir */
    .stButton button,
    .stButton > button,
    div[data-testid="column"] button,
    .element-container button,
    [data-testid="stButton"] button,
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #6A1B9A, #8E24AA) !important;
        color: white !important;
        border-radius: 15px !important;
        height: 80px !important;
        width: 100% !important;
        min-width: 350px !important;
        max-width: 350px !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        border: 2px solid rgba(106, 27, 154, 0.4) !important;
        box-shadow: 0 6px 20px rgba(106, 27, 154, 0.4) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }

    .stButton button:hover,
    .stButton > button:hover,
    div[data-testid="column"] button:hover,
    .element-container button:hover,
    [data-testid="stButton"] button:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #7B1FA2, #9C27B0) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(106, 27, 154, 0.5) !important;
        border-color: rgba(106, 27, 154, 0.6) !important;
        color: white !important;
    }

    .stButton button:active,
    .stButton > button:active,
    div[data-testid="column"] button:active,
    .element-container button:active,
    [data-testid="stButton"] button:active,
    button[data-testid="baseButton-secondary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 3px 12px rgba(106, 27, 154, 0.4) !important;
        background: linear-gradient(135deg, #5E1A87, #7B1FA2) !important;
        color: white !important;
    }

    /* Buton kolonlarını da ayarla */
    div[data-testid="column"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* Dataset info section */
    .dataset-info-section {
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        padding: 0.5rem 0;
    }
    .dataset-info-section h3 {
        font-size: 2.2rem;
        margin-bottom: 1rem;
        color: #96ceb4;
        text-align: left;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .dataset-info-section ul {
        list-style-type: none;
        padding-left: 0;
        margin: 0;
        max-width: 600px;
    }
    .dataset-info-section li {
        margin-bottom: 0.6rem;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        text-align: left;
        padding-left: 0;
        color: #d0d0d0;
    }
    .dataset-info-section li strong {
        color: #ffeaa7;
        margin-right: 10px;
    }
    .dataset-info-section .emoji {
        font-size: 1.5em;
        margin-right: 15px;
        line-height: 1;
    }

    /* Footer section */
    .footer-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }
    .footer-section h3 {
        font-size: 1.6rem;
        margin-bottom: 0.8rem;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .footer-section p {
        font-size: 0.95rem;
        line-height: 1.5;
        opacity: 0.9;
    }

    /* Sidebar styles */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2a2a3e 0%, #1a1a2e 100%);
        color: #e0e0e0;
    }
    .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
        color: #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Başlık ve Logo Bölümü ---
# Ana başlık ve logo için iki sütun oluştur, aralarında boşluk olmadan
col_left, col_right = st.columns([0.7, 0.3]) # Oranları istediğiniz gibi ayarlayabilirsiniz

with col_left:
    st.markdown('<div class="text-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🏠 Hoş Geldiniz, MovieX AI Sizinle!</h1>', unsafe_allow_html=True)
    st.markdown("""
        <div class="welcome-section">
            <p>Bu uygulama, film verisi üzerinde <b>makine öğrenmesi ve öneri sistemi</b> yaklaşımlarını kullanarak geliştirilmiştir.</p>
            <p>Aşağıdaki sayfalara doğrudan gitmek için ilgili butona tıklayabilir veya sol menüyü kullanabilirsiniz.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("img_2.png", width=200, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Navigasyon Başlığı ve Butonlar ---
st.markdown("""
<div class="navigation-question">
    <h3 style="color: #bb6aee;">Hangi bölüme gitmek istersiniz?</h3>
</div>
""", unsafe_allow_html=True)

# Butonlar - tam ortada, eşit boyutta
st.markdown('<div class="button-row">', unsafe_allow_html=True)

# Üç sütun oluştur
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    if st.button("📜 Veri Seti Hikayesi", key="btn1", help="Veri setinin detaylı incelemesine gidin."):
        st.switch_page("pages/Dataset_Story.py")

with col2:
    if st.button("📊 Film Rating Tahmini", key="btn2", help="Filmlerin IMDB puanını tahmin edin."):
        st.switch_page("pages/Rating_Tahmini.py")

with col3:
    if st.button("🎥 Film Öneri Sistemi", key="btn3", help="Benzer filmler için öneriler alın."):
        st.switch_page("pages/Öneri_Sistemi.py")

st.markdown('</div>', unsafe_allow_html=True)

# --- Ayırıcı Çizgi ---
st.markdown("---")

# --- Kullanılan Veri Seti Bölümü ---
st.markdown("""
<div class="dataset-info-section">
    <h3>📁 Kullanılan Veri Seti</h3>
    <ul>
        <li><span class="emoji">📚</span> <strong>Veri seti:</strong> <code>AllMoviesDetailsCleaned.csv</code></li>
        <li><span class="emoji">🔗</span> <strong>Kaynak:</strong> TMDB + IMDB birleşik verisi</li>
        <li><span class="emoji">📊</span> <strong>Veri boyutu:</strong> 75.000+ film</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- Altbilgi ---
st.markdown("---")
st.markdown("""
<div class="footer-section">
    <h3>🎬 Film Projesi</h3>
    <p>Veri Bilimi ve Makine Öğrenmesi ile Sinemayı Keşfedin</p>
    <p>📧 İletişim: info@filmanalytics.com | 🌐 Website: www.filmanalytics.com</p>
</div>
""", unsafe_allow_html=True)
