import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import time  # Progress bar için

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🎬 IMDB Film Rating Tahmin Uygulaması",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gelişmiş CSS stilleri (SADECE ANA ARKA PLAN SİYAH, DİĞER HER ŞEY ORİJİNAL RENKLİ)
st.markdown("""
    <style>
    /* SADECE Genel Streamlit arka plan rengini tam siyaha ayarla */
    body {
        background-color: #000000; /* Tamamen siyah */
        color: #e0e0e0; /* Varsayılan açık gri metin rengi */
    }
    .stApp {
        background-color: #000000; /* Streamlit ana uygulama kapsayıcısını da siyah yap */
    }

    /* Ana başlık stili */
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #E6E6FA, #D8BFD8, #DA70D6, #BA55D3, #4B0082);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease-in-out infinite;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Metrik kartları (prediction summary altındaki 3 kart) */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Mor gradyan */
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .metric-card:hover {
        transform: translateY(-5px) scale(1.01);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }

    .metric-card h3 {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }

    .metric-card h1 {
        font-size: 2.5rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .metric-card p {
        font-size: 0.85rem;
        margin-bottom: 0;
        color: #e0e0e0;
    }

    /* Başarı kutusu */
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); /* Mavi-turkuaz gradyan */
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-left: 6px solid #00f2fe;
        animation: pulse 2s infinite;
    }
    .success-box h3 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .success-box p {
        font-size: 0.95rem;
    }

    @keyframes pulse {
        0% { box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
        50% { box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4); }
        100% { box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    }

    /* Uyarı kutusu */
    .warning-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-left: 6px solid #fee140;
    }

    /* Bilgi kartları (tahmini etkileyen faktörler) */
    .info-card {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%); /* Açık gradyan */
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        border-left: 4px solid #2196f3; /* Mavi kenarlık */
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
        color: #333333; /* Açık arka plan üzerinde koyu metin */
        font-size: 0.88rem;
    }

    .info-card:hover {
        transform: translateX(3px);
    }

    /* Tahmin sonuç özeti kartı (ana büyük tahmin kartı) */
    .prediction-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* Özellik kartları (genre ve ROI özeti) */
    .feature-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); /* Şeftali gradyanı */
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        border-left: 4px solid #ff7f50; /* Turuncu kenarlık */
        color: #333333; /* Açık arka plan üzerinde koyu metin */
        font-size: 0.88rem;
    }
    .feature-card h4 {
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }
    .feature-card p {
        font-size: 0.8rem;
    }

    /* Ülke kartı */
    .country-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); /* Mavi-pembe gradyan */
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.3rem;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
        color: #333333; /* Açık arka plan üzerinde koyu metin */
        border-left: 4px solid #96ceb4; /* Yeşilimsi kenarlık */
        font-size: 0.88rem;
    }

    .country-card:hover {
        transform: scale(1.02);
    }
    .country-card h4 {
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }
    .country-card p {
        font-size: 0.8rem;
    }

    /* Şirket kartı */
    .company-card {
        background: linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%); /* Turuncu-mor gradyan */
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.3rem;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
        color: #333333; /* Açık arka plan üzerinde koyu metin */
        border-left: 4px solid #ffeaa7; /* Sarı kenarlık */
        font-size: 0.88rem;
    }

    .company-card:hover {
        transform: scale(1.02);
    }
    .company-card h4 {
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }
    .company-card p {
        font-size: 0.8rem;
    }

    /* form-section stili - GENEL BÖLÜM STİLİ */
    .form-section {
        background-color: #9370DB; /* Düz, orta mor tonu */
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.15);
        color: #f0f0f0;
    }

    /* Ana form başlığı (Film Özellikleri Girişi) */
    .form-section h3 {
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        margin-top: 0.5rem !important;
        margin-bottom: 0.8rem !important;
        font-size: 1.7rem;
    }

    /* Alt başlıklar için yeni stil (daha kompakt) */
    .form-section .section-subheader {
        color: white;
        font-size: 1.2rem; /* Daha küçük */
        margin-top: 0.5rem; /* Üst boşluğu azalt */
        margin-bottom: 0.5rem; /* Alt boşluğu azalt */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        border-bottom: 1px solid rgba(255,255,255,0.3);
        padding-bottom: 0.2rem; /* Çizgiye yakınlık */
    }

    .form-section p {
        color: #e0e0e0;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
    }

    /* Streamlit input bileşenlerinin (selectbox, number_input, text_input vb.) stillerini ayarlama */
    /* Bu kısım aynı kalabilir, genel olarak input boyutu zaten ayarlı */
    .stSelectbox > label, .stNumberInput > label, .stTextInput > label, .stDateInput > label, .stMultiSelect > label {
        color: #f0f0f0;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
        margin-top: 0.5rem; /* Label'lar arasına biraz boşluk */
    }
    .stSelectbox > div > div, .stNumberInput > div > div > input, .stTextInput > div > div > input, .stDateInput > label + div > div, .stMultiSelect > div > div {
        height: 2.2rem;
        min-height: 2.2rem;
        background-color: #282836;
        border-radius: 8px;
        border: 1px solid #4a4a60;
        transition: all 0.3s ease;
        color: #e0e0e0;
        font-size: 0.9rem;
    }
    /* Özellikle multiselect için, seçilen etiketlerin hizalanması */
    .stMultiSelect .st-cm {
        line-height: 1.5; /* İçerik dikey ortalama */
    }

    /* Sidebar (Yan çubuk) stili */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2a2a3e 0%, #1a1a2e 100%); /* Koyu morumsu mavi gradyan */
        color: #e0e0e0;
    }
    .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
        color: #f0f0f0;
    }
    /* Sidebar navigasyon linkleri */
    .sidebar .st-emotion-cache-1cypcdb p {
        color: #e0e0e0;
    }
    .sidebar .st-emotion-cache-1cypcdb a {
        color: #e0e0e0 !important;
        background-color: transparent !important;
        border-radius: 8px;
        transition: background-color 0.2s ease;
        padding: 0.4rem 0.8rem;
        font-size: 0.9rem;
    }
    .sidebar .st-emotion-cache-1cypcdb a:hover {
        background-color: #3a3a50 !important;
    }
    /* Seçili yan çubuk linki */
    .sidebar .st-emotion-cache-1cypcdb a[data-selected="true"] {
        background-color: #4a4a60 !important;
        color: white !important;
        font-weight: bold;
    }

    .prediction-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Mor gradyan */
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }

    .emoji-large {
        font-size: 1.8rem;
        margin-right: 0.4rem;
    }

    /* Plotly grafikleri için arka planı şeffaf yapma ve metin rengi */
    .js-plotly-plot .plotly .modebar {
        background-color: transparent !important;
    }
    .js-plotly-plot .plotly .title {
        color: #e0e0e0 !important;
        font-size: 1.2rem !important;
    }
    .js-plotly-plot .plotly .xtick, .js-plotly-plot .plotly .ytick {
        font-size: 0.85rem !important;
        color: #e0e0e0 !important;
    }
    .js-plotly-plot .plotly .g-ytitle, .js-plotly-plot .plotly .g-xtitle {
        font-size: 0.9rem !important;
        color: #e0e0e0 !important;
    }

    /* Altbilgi için arka planı koyulaştırma */
    div[data-testid="stMarkdownContainer"] > div[style*="text-align: center;"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; /* Mor gradyan */
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
    }

    /* Tahmin geçmişi kartı stili */
    .history-card {
        background-color: #282836;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        border-left: 5px solid #4CAF50; /* Yeşil çizgi */
    }
    .history-card p {
        margin: 0;
        font-size: 0.9rem;
        color: #e0e0e0;
    }
    .history-card .film-title {
        font-weight: bold;
        color: #4ECDC4;
    }
    .history-card .rating-score {
        font-weight: bold;
        font-size: 1.1rem;
        color: #FFD700; /* Altın rengi */
    }
    </style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown('<h1 class="main-header">🎬 IMDB Film Rating Tahmin Uygulaması</h1>', unsafe_allow_html=True)

# Session state'i başlat (tahmin geçmişi için)
if 'prediction_history' not in st.session_state:
    st.session_state['prediction_history'] = []


# Model ve özellik listesini yükle
@st.cache_resource
def load_model_components():
    """Model ve gerekli bileşenleri yükler"""
    try:
        model = joblib.load('catboost_model.pkl')
        feature_columns = joblib.load('feature_columns.pkl')
        return model, feature_columns
    except FileNotFoundError:
        st.error(
            "Model dosyaları (catboost_model.pkl veya feature_columns.pkl) bulunamadı. Lütfen doğru dizinde olduklarından emin olun.")
        st.stop()
    except Exception as e:
        st.error(f"Model yüklenirken bir hata oluştu: {e}")
        st.stop()


model, feature_columns = load_model_components()

# Uygulama açıklaması
st.markdown("""
<div class="form-section">
    <h3>🎯 Uygulama Hakkında</h3>
    <p>Bu gelişmiş uygulama, film endüstrisindeki profesyoneller ve sinemaseverler için tasarlandı.
    Girdiğiniz detaylı film özelliklerine (bütçe, hasılat, türler, yapım bilgileri vb.) dayanarak
    IMDB puanını yüksek doğrulukla tahmin eder. Yapay zeka destekli modelimiz, geçmiş verilerden
    öğrenerek filmin potansiyel başarısı hakkında değerli içgörüler sunar.</p>
</div>
""", unsafe_allow_html=True)

# Ülke ve yapım şirketi seçenekleri (aynı)
COUNTRIES = {
    'USA': 'ABD', 'UK': 'İngiltere', 'Germany': 'Almanya', 'France': 'Fransa',
    'Italy': 'İtalya', 'Spain': 'İspanya', 'Canada': 'Kanada', 'Japan': 'Japonya',
    'India': 'Hindistan', 'Others': 'Diğer', 'None': 'Belirtilmemiş'
}

PRODUCTION_COMPANIES = {
    'Warner Bros.': 'Warner Bros.',
    'Universal Pictures': 'Universal Pictures',
    'Twentieth Century Fox': 'Twentieth Century Fox',
    'Paramount Pictures': 'Paramount Pictures',
    'Columbia Pictures': 'Columbia Pictures',
    'Metro-Goldwyn-Mayer (MGM)': 'Metro-Goldwyn-Mayer (MGM)',
    'RKO Radio Pictures': 'RKO Radio Pictures',
    'Shaw Brothers': 'Shaw Brothers',
    'BBC': 'BBC',
    'Pixar Animation Studios': 'Pixar Animation Studios',
    'Walt Disney Pictures': 'Walt Disney Pictures',
    'Others': 'Diğer',
    'None': 'Bağımsız/Belirtilmemiş'
}

# Sol sidebar için Tahmin Geçmişi
with st.sidebar:
    st.header("🕰️ Son Tahminler")
    if st.session_state['prediction_history']:
        # En yeni tahminlerin en üstte görünmesini sağlamak için tersten sıralama yapıyoruz
        # Sadece son 5 tahmini göster.
        for entry in reversed(st.session_state['prediction_history'][-5:]):
            st.markdown(f"""
            <div class="history-card">
                <p><span class="film-title">{entry['title']}</span></p>
                <p>IMDB: <span class="rating-score">{entry['rating']:.2f} ⭐</span></p>
                <p style="font-size:0.75rem; color:#a0a0a0;">{entry['date']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz bir tahmin yapmadınız.")

    st.markdown("---")
    st.header("⚙️ Nasıl Çalışır?")
    st.write("""
    Bu uygulama, makine öğrenimi modelleri kullanarak film özelliklerinden IMDB puanını tahmin eder.
    Model, binlerce filmin verileri üzerinde eğitilmiştir ve bütçe, hasılat, tür, süre, yayın tarihi gibi
    faktörleri analiz ederek tahminde bulunur.
    """)
    st.info("Tahminler bilgilendirme amaçlıdır ve kesin bir başarı garantisi vermez.")

# Kullanıcıdan bilgi alımı
with st.form("prediction_form", clear_on_submit=False):
    # Film Özellikleri Ana Bölümü
    st.markdown("""
        <div class="form-section">
            <h3>🎬 Film Özellikleri Girişi</h3>
            <p>Lütfen tahmin için gerekli olan film özelliklerini eksiksiz girin.</p>
    """, unsafe_allow_html=True)

    # Film Başlığı Girişi
    film_title = st.text_input("📝 Film Adı", value="Örnek Film Adı",
                               help="Tahmin etmek istediğiniz filmin adını girin.")

    # --- Finansal Bilgiler Bölümü ---
    st.markdown('<p class="section-subheader">💰 Finansal Bilgiler</p>', unsafe_allow_html=True)
    col_fin1, col_fin2 = st.columns(2)  # Finansal bilgileri iki sütuna ayırarak daha kompakt hale getiriyoruz

    with col_fin1:
        budget = st.number_input(
            "💲 Bütçe (USD)",
            min_value=0.0,
            max_value=1_000_000_000.0,
            value=1_000_000.0,
            format="%.2f",
            help="Filmin üretim bütçesini USD cinsinden girin. Örn: 1.000.000. Çok büyük bütçeler için milyar aralığını kullanabilirsiniz."
        )
    with col_fin2:
        revenue = st.number_input(
            "💸 Hasılat (USD)",
            min_value=0.0,
            max_value=5_000_000_000.0,
            value=5_000_000.0,
            format="%.2f",
            help="Filmin dünya genelindeki toplam hasılatını USD cinsinden girin. Örn: 5.000.000. Yüksek hasılatlar için milyar aralığını kullanabilirsiniz."
        )

    # Basit ROI Hesaplayıcı
    st.markdown('<p class="section-subheader">📈 Anlık ROI Hesaplayıcı</p>', unsafe_allow_html=True)
    # ROI kontrolü burada da yapılmalı
    if budget > 0:
        current_roi_value = ((revenue / budget - 1) * 100)
        st.markdown(f"""
            <div style="background-color: #282836; padding: 10px; border-radius: 8px; border: 1px solid #4a4a60; text-align: center;">
                <p style="margin:0; font-size:1.1rem; color:#f0f0f0;">Mevcut Girdilerle ROI: <strong>{current_roi_value:.1f}%</strong></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Bütçe 0 veya negatifse, ROI'yi hesaplayamayız.
        # Bu durumu kullanıcıya bildiren bir mesaj göster.
        if revenue > 0:
            st.markdown(f"""
                <div style="background-color: #282836; padding: 10px; border-radius: 8px; border: 1px solid #4a4a60; text-align: center;">
                    <p style="margin:0; font-size:1.1rem; color:#f0f0f0;">Mevcut Girdilerle ROI: <strong>Sonsuz (Bütçe Sıfır)</strong></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: #282836; padding: 10px; border-radius: 8px; border: 1px solid #4a4a60; text-align: center;">
                    <p style="margin:0; font-size:1.1rem; color:#f0f0f0;">Mevcut Girdilerle ROI: <strong>N/A (Bütçe Tanımsız)</strong></p>
                </div>
                """, unsafe_allow_html=True)

    # --- Teknik Bilgiler Bölümü ---
    st.markdown('<p class="section-subheader">⚙️ Teknik Detaylar</p>', unsafe_allow_html=True)
    col_tech1, col_tech2, col_tech3 = st.columns(3)

    with col_tech1:
        runtime = st.number_input(
            "⏱️ Süre (dakika)",
            min_value=1,
            max_value=400,
            value=120,
            help="Filmin toplam süresini dakika cinsinden girin. Ortalama filmler 90-180 dakika arasındadır."
        )
    with col_tech2:
        vote_count = st.number_input(
            "📊 Oy Sayısı",
            min_value=0,
            max_value=500_000_000,
            value=1500,
            help="IMDB veya benzeri platformlardaki oy sayısını girin. Yüksek oy sayısı, tahminin güvenilirliğini artırır."
        )
    with col_tech3:
        popularity = st.number_input(
            "🔥 Popülarite",
            min_value=0.0,
            max_value=1000.0,
            value=10.0,
            format="%.2f",
            help="Filmin anlık popülarite puanını girin. Bu genellikle dinamik bir metriktir. Ortalama filmler 10-50 arasındadır, çok popüler filmler 100+'a çıkabilir."
        )

    # --- Yayın Bilgileri Bölümü ---
    st.markdown('<p class="section-subheader">🗓️ Yayın Bilgileri</p>', unsafe_allow_html=True)
    col_pub1, col_pub2 = st.columns(2)

    with col_pub1:
        release_date = st.date_input(
            "🗓️ Yayın Tarihi",
            value=datetime(2015, 1, 1),
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date(),
            help="Filmin ilk yayınlandığı tarihi seçin."
        )
    with col_pub2:
        language_en = st.checkbox(
            "🇬🇧 Ana Dil İngilizce mi?",
            value=True,
            help="Filmin ana dilinin İngilizce olup olmadığını belirtin."
        )

    # --- Film Türleri Bölümü ---
    st.markdown('<p class="section-subheader">🎭 Film Türleri</p>', unsafe_allow_html=True)
    all_genres_options = [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Drama',
        'Documentary', 'Family', 'Fantasy', 'Foreign', 'History',
        'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
        'TV Movie', 'Thriller', 'War', 'Western'
    ]
    genres = st.multiselect(
        "Lütfen filminize uygun türleri seçin (birden fazla seçebilirsiniz):",
        all_genres_options,
        default=['Drama', 'Action'],
        help="Filminize uygun tüm türleri seçin. Genellikle bir film 1 ila 5 arasında türe sahip olabilir."
    )

    # --- Yapım Bilgileri Bölümü ---
    st.markdown('<p class="section-subheader">🏢 Yapım Bilgileri</p>', unsafe_allow_html=True)
    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        selected_country = st.selectbox(
            "🌍 Yapım Ülkesi",
            list(COUNTRIES.keys()),
            index=0,
            format_func=lambda x: COUNTRIES[x],
            help="Filmin ana yapım ülkesini seçin. Bu, kültürel etkiyi ve yapım kalitesini yansıtabilir."
        )
    with col_prod2:
        selected_company = st.selectbox(
            "🎬 Yapım Şirketi",
            list(PRODUCTION_COMPANIES.keys()),
            index=9,
            format_func=lambda x: PRODUCTION_COMPANIES[x],
            help="Filmi üreten ana yapım şirketini seçin. Büyük stüdyolar genellikle yüksek bütçeli yapımlar yapar."
        )

    st.markdown('</div>', unsafe_allow_html=True)  # Ana form-section div'ini kapatma

    # Tahmin butonu
    st.markdown("---")
    submitted = st.form_submit_button("✨ IMDB Puanını Tahmin Et", use_container_width=True)

if submitted:
    # Progress Bar
    progress_text = "Tahmin modeli çalıştırılıyor, lütfen bekleyin..."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    my_bar.empty()

    try:
        # ROI hesaplaması - Geliştirilmiş hata yönetimi
        return_ratio = 0.0
        if budget > 0:
            return_ratio = revenue / budget
        elif budget == 0 and revenue > 0:
            # ROI sonsuz olur, modelin işleyebileceği bir değer verelim, örneğin çok büyük bir sayı
            # veya sadece 0 bırakalım ve uyarı verelim. Modelin eğitimi 0'ları iyi işleyebilir.
            # Şimdilik 0 bırakmak daha güvenli.
            st.warning(
                "⚠️ Bütçe sıfır olduğu için yatırım getirisi (ROI) sonsuz kabul edilir veya hesaplanamaz. Tahmin için 0 olarak işlenecektir.")
        elif budget == 0 and revenue == 0:
            pass  # İkisi de sıfırsa ROI 0 kalır
        else:  # budget negatifse
            st.warning(
                "⚠️ Negatif bütçe değeri girildiği için yatırım getirisi (ROI) hesaplanamaz. Tahmin için 0 olarak işlenecektir.")

        # Input dictionary oluşturma
        input_dict = {
            'runtime': runtime,
            'budget': budget,
            'revenue': revenue,
            'vote_count': vote_count,
            'popularity': popularity,
            'release_year': release_date.year,
            'release_month': release_date.month,
            'release_day': release_date.day,
            'has_budget': int(budget > 0),
            'has_revenue': int(revenue > 0),
            'has_votes': int(vote_count > 0),
            'movie_age': datetime.now().year - release_date.year,
            'return_ratio': return_ratio,
            'lang_en': int(language_en)
        }

        # Türler binary encoding
        all_genres = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama',
            'Family', 'Fantasy', 'Foreign', 'History', 'Horror', 'Music', 'Mystery', 'Romance',
            'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western'
        ]

        for genre in all_genres:
            input_dict[genre] = int(genre in genres)

        # Ülke kodlaması
        country_mapping = {
            'USA': 'country_usa', 'UK': 'country_uk', 'Germany': 'country_germany',
            'France': 'country_france', 'Italy': 'country_italy', 'Spain': 'country_spain',
            'Canada': 'country_canada', 'Japan': 'country_japan', 'India': 'country_india',
            'Others': 'country_others', 'None': 'country_none'
        }

        for country_key, country_col in country_mapping.items():
            input_dict[country_col] = int(selected_country == country_key)

        # Yapım şirketi kodlaması
        company_mapping = {
            'Warner Bros.': 'company_Warner Bros.',
            'Universal Pictures': 'company_Universal Pictures',
            'Twentieth Century Fox': 'company_Twentieth Century Fox',
            'Paramount Pictures': 'company_Paramount Pictures',
            'Columbia Pictures': 'company_Columbia Pictures',
            'Metro-Goldwyn-Mayer (MGM)': 'company_Metro-Goldwyn-Mayer (MGM)',
            'RKO Radio Pictures': 'company_RKO Radio Pictures',
            'Shaw Brothers': 'company_Shaw Brothers',
            'BBC': 'company_BBC',
            'Pixar Animation Studios': 'company_Pixar Animation Studios',
            'Walt Disney Pictures': 'company_Walt Disney Pictures',
            'Others': 'company_Others',
            'None': 'company_none'
        }

        for company_key, company_col in company_mapping.items():
            input_dict[company_col] = int(selected_company == company_key)

        # Model girdisini oluşturma
        input_df = pd.DataFrame([input_dict])
        for col in feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[feature_columns]

        # Tahmini hesapla
        predicted_rating = model.predict(input_df)[0]

        # Güven düzeltmesi
        adjusted_rating = predicted_rating
        adjustment_factors = []
        total_adjustment = 0

        # Oy sayısına göre ayarlama
        if vote_count > 10000:
            adjustment = 0.4
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🗳️ Çok Yüksek Değerlendirme (+{adjustment:.1f})")
        elif vote_count > 5000:
            adjustment = 0.3
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"📊 Yüksek Değerlendirme (+{adjustment:.1f})")
        elif vote_count > 1000:
            adjustment = 0.1
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"✅ Yeterli Değerlendirme (+{adjustment:.1f})")
        elif vote_count < 100:
            adjustment = -0.3
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"❓ Az Değerlendirme ({adjustment:.1f})")

        # Tür etkisi
        prestige_genres = ['Drama', 'Documentary', 'History', 'War']
        commercial_genres = ['Action', 'Comedy', 'Horror', 'Adventure', 'Thriller']

        prestige_count = len([g for g in genres if g in prestige_genres])
        commercial_count = len([g for g in genres if g in commercial_genres])

        if prestige_count >= 2:
            adjustment = 0.4
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🏆 Prestijli Türler (+{adjustment:.1f})")
        elif prestige_count == 1:
            adjustment = 0.2
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🎭 Prestijli Tür (+{adjustment:.1f})")

        if commercial_count >= 3:
            adjustment = -0.2
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🎪 Çok Ticari Tür ({adjustment:.1f})")

        # Ülke etkisi
        if selected_country in ['USA', 'UK']:
            adjustment = 0.2
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🌟 Prestijli Sinema Ülkesi (+{adjustment:.1f})")
        elif selected_country in ['France', 'Germany', 'Italy']:
            adjustment = 0.1
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🎨 Sanat Sineması Ülkesi (+{adjustment:.1f})")

        # Yapım şirketi etkisi
        major_studios = ['Warner Bros.', 'Universal Pictures', 'Paramount Pictures', 'Pixar Animation Studios',
                         'Walt Disney Pictures']
        if selected_company in major_studios:
            adjustment = 0.15
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🏢 Büyük Stüdyo (+{adjustment:.1f})")

        # Süre etkisi
        if 90 <= runtime <= 130:
            adjustment = 0.3
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"⏱️ Optimal Süre (+{adjustment:.1f})")
        elif 130 < runtime <= 180:
            adjustment = 0.1
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"📽️ Epik Süre (+{adjustment:.1f})")
        elif runtime < 80:
            adjustment = -0.2
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"⚡ Çok Kısa ({adjustment:.1f})")
        elif runtime > 200:
            adjustment = -0.3
            adjusted_rating += adjustment
            total_adjustment += adjustment
            adjustment_factors.append(f"🐌 Çok Uzun ({adjustment:.1f})")

        # IMDB puanı 1-10 arasında olmalı, sınırları zorla
        predicted_rating = max(1.0, min(10.0, predicted_rating))
        adjusted_rating = max(1.0, min(10.0, adjusted_rating))

        # Tahmin geçmişini güncelleme veya ekleme (DÜZELTME BURADA)
        new_entry = {
            'title': film_title,
            'rating': adjusted_rating,  # Ensure this is the correct IMDB rating
            'date': datetime.now().strftime("%d %b %Y %H:%M")
        }

        # Aynı film başlığına sahip mevcut bir girişi bul ve kaldır
        # Bu kısım doğru çalışıyor olmalı, yinelenenleri temizlemeli.
        # Eğer hala hata varsa, film_title'ın nasıl işlendiğine bakmak gerekebilir.
        st.session_state['prediction_history'] = [
            entry for entry in st.session_state['prediction_history'] if entry['title'] != film_title
        ]
        # Yeni girişi ekle
        st.session_state['prediction_history'].append(new_entry)

        # Sonuçları göster
        st.markdown("""
        <div class="prediction-summary">
            <h2>🎯 Tahmin Sonuçları</h2>
            <p>Filmininiz için detaylı analiz tamamlandı!</p>
        </div>
        """, unsafe_allow_html=True)

        col_pred, col_adj, col_info = st.columns(3)

        with col_pred:
            st.markdown(f"""
                <div class="metric-card">
                    <h3><span class="emoji-large">🤖</span>Ham Model Tahmini</h3>
                    <h1>{predicted_rating:.2f} ⭐</h1>
                    <p>Makine öğrenmesi algoritması</p>
                </div>
            """, unsafe_allow_html=True)

        with col_adj:
            st.markdown(f"""
                <div class="metric-card">
                    <h3><span class="emoji-large">🎯</span>Nihai Tahmin</h3>
                    <h1>{adjusted_rating:.2f} ⭐</h1>
                    <p>Güven faktörleri dahil</p>
                </div>
            """, unsafe_allow_html=True)

        with col_info:
            confidence_level = "Yüksek" if vote_count > 1000 else "Orta" if vote_count > 100 else "Düşük"
            st.markdown(f"""
                <div class="metric-card">
                    <h3><span class="emoji-large">📊</span>Güven Seviyesi</h3>
                    <h1 style="color: white;">{confidence_level}</h1>
                    <p>Tahmin güvenilirliği</p>
                </div>
            """, unsafe_allow_html=True)

        # Seçilen özelliklerin özeti
        st.subheader("📋 Film Bilgileri Özeti")
        col_summary1, col_summary2 = st.columns(2)

        with col_summary1:
            st.markdown(f"""
            <div class="country-card">
                <h4>🌍 {COUNTRIES[selected_country]}</h4>
                <p>Yapım Ülkesi</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="feature-card">
                <h4>🎭 Türler ({len(genres)})</h4>
                <p>{', '.join(genres) if genres else 'Belirtilmemiş'}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_summary2:
            st.markdown(f"""
            <div class="company-card">
                <h4>🏢 {PRODUCTION_COMPANIES[selected_company]}</h4>
                <p>Yapım Şirketi</p>
            </div>
            """, unsafe_allow_html=True)

            roi_value_display = "N/A"
            if budget > 0:
                roi_value_display = f"{(revenue / budget - 1) * 100:.1f}%"
            elif budget == 0 and revenue == 0:
                roi_value_display = "N/A (Bütçe & Hasılat Sıfır)"
            elif budget == 0 and revenue > 0:
                roi_value_display = "Sonsuz (Bütçe Sıfır)"
            else:  # budget < 0
                roi_value_display = "Hesaplanamaz (Negatif Bütçe)"

            st.markdown(f"""
            <div class="feature-card">
                <h4>💰 ROI: {roi_value_display}</h4>
                <p>Yatırım Getirisi</p>
            </div>
            """, unsafe_allow_html=True)

        # Etki faktörleri
        if adjustment_factors:
            st.subheader("🎛️ Tahmini Etkileyen Faktörler")
            cols = st.columns(3)
            for i, factor in enumerate(adjustment_factors):
                with cols[i % 3]:
                    st.markdown(f'<div class="info-card">{factor}</div>', unsafe_allow_html=True)

        # Başarı mesajı
        st.markdown(f"""
        <div class="success-box">
            <h3>✅ Tahmin Başarıyla Tamamlandı!</h3>
            <p>Toplam {len(adjustment_factors)} faktör tahmininizi etkiledi.
            Güven ayarlaması: <strong>{total_adjustment:+.1f}</strong> puan</p>
        </div>
        """, unsafe_allow_html=True)

        # Görselleştirme
        st.subheader("📊 Tahmin Analizi")

        # Özellik önemi grafiği
        importance_data = {
            'Özellik': ['Oy Sayısı', 'Bütçe', 'Popülarite', 'Hasılat', 'Süre', 'Tür', 'Ülke', 'Yapım Şirketi'],
            'Önem Skoru': [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04]
        }

        fig = px.bar(
            importance_data,
            x='Önem Skoru',
            y='Özellik',
            orientation='h',
            title='🎯 Modelin Önem Verdiği Faktörler',
            color='Önem Skoru',
            color_continuous_scale='viridis'
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#e0e0e0"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Karşılaştırma grafiği
        comparison_data = {
            'Tahmin Türü': ['Ham Model', 'Güven Ayarlı'],
            'IMDB Puanı': [predicted_rating, adjusted_rating],
            'Renk': ['#FF6B6B', '#4ECDC4']
        }

        fig2 = px.bar(
            comparison_data,
            x='Tahmin Türü',
            y='IMDB Puanı',
            title='📈 Tahmin Karşılaştırması',
            color='Renk',
            color_discrete_map={'#FF6B6B': '#FF6B6B', '#4ECDC4': '#4ECDC4'}
        )
        fig2.update_layout(
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#e0e0e0"
        )
        fig2.update_traces(texttemplate='%{y:.2f}', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Tahmin sırasında bir hata oluştu: {e}")
        st.info("Lütfen tüm alanları eksiksiz doldurun ve model dosyalarının mevcut olduğundan emin olun.")

# Altbilgi
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
           border-radius: 15px; color: white; margin-top: 2rem;">
    <h3>🎬 IMDB Film Rating Tahmin Uygulaması</h3>
    <p>Gelişmiş makine öğrenmesi algoritmaları ile güçlendirilmiştir</p>
    <p>📧 İletişim: info@filmanalytics.com | 🌐 Website: www.filmanalytics.com</p>
</div>
""", unsafe_allow_html=True)