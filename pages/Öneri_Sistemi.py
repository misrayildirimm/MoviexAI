import streamlit as st
import pandas as pd
import time
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.graph_objects as go

# set_page_config() her Streamlit dosyasında (sayfasında)
# SADECE BİR KEZ ve İLK STREAMLIT KOMUTU olarak çağrılmalıdır.
st.set_page_config(page_title="🎬 Film Öneri Sistemi ", layout="wide", page_icon="🎬")

# TMDb API anahtarınızı buraya girin
TMDB_API_KEY = "488f81afa52261bcc296a469f28f54dc"

# 🌈 Gelişmiş Özel Stil
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

    /* Alt başlıklar için stil */
    .subheader-gradient {
        font-size: 1.8rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Gelişmiş Film Kartı (Öneri Sonuçları) */
    .movie-card {
        background: linear-gradient(135deg, #5e17eb 0%, #8d48e0 100%);
        padding: 20px;
        margin: 15px 0;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        color: white;
        display: flex;
        align-items: flex-start;
        transition: all 0.3s ease-in-out;
        border: 1px solid rgba(255,255,255,0.15);
        position: relative;
        overflow: hidden;
    }

    .movie-card:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }

    .movie-card:hover:before {
        left: 100%;
    }

    .movie-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 35px rgba(0,0,0,0.5);
    }

    .movie-poster {
        margin-right: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        min-width: 100px;
        max-width: 100px; /* Sabit genişlik */
        height: 150px; /* Orantılı yükseklik */
        object-fit: cover; /* Resmin kutuya sığmasını sağlar */
    }

    .movie-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .movie-title {
        font-size: 1.4em;
        font-weight: bold;
        margin: 0 0 8px 0;
        color: #FFD700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }

    .movie-genres {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 5px 0;
    }

    .genre-tag {
        background: rgba(255, 215, 0, 0.2);
        color: #FFD700;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }

    .movie-stats {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 8px 0;
        flex-wrap: wrap;
    }

    .stat-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 0.9em;
        color: #e0e0e0;
    }

    .rating-high { color: #4CAF50; }
    .rating-medium { color: #FF9800; }
    .rating-low { color: #F44336; }

    .movie-overview {
        font-size: 0.95em;
        line-height: 1.4;
        color: #d0d0d0;
        margin-top: 8px;
        max-height: 60px; /* Özetin tek bir satıra sığması için */
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: normal; /* Metnin normal akışını koru */
        display: -webkit-box;
        -webkit-line-clamp: 3; /* Maksimum 3 satır */
        -webkit-box-orient: vertical;
    }

    /* Filtre ve Kontrol Paneli (Geliştirilmiş - Dış Kutuyu Kaldırdık) */
    .filter-group-label {
        color: #FFD700;
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
    }

    /* Buton Stilleri */
    .stButton>button {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: black;
        border-radius: 10px;
        height: 3.5em;
        width: 100%;
        font-size: 1.1em;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #FFA500, #FFD700);
    }

    /* Selectbox Stilleri */
    .stSelectbox > label { /* Streamlit'in otomatik label'ını gizle */
        display: none !important;
    }
    .stSelectbox > div > div {
        background-color: #282836;
        border-radius: 8px;
        border: 1px solid #4a4a60;
        transition: all 0.3s ease;
        color: #e0e0e0;
        font-size: 0.9rem;
        height: 2.5rem;
        min-height: 2.5rem;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #FFD700;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.3);
    }
    .stSelectbox .st-cg { /* Dropdown okunun rengini ayarlamak */
        color: #FFD700;
    }

    /* Metrik Kartları */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        margin: 5px;
    }

    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }

    /* Seçilen Film Detay Kartı (YENİ VE GELİŞTİRİLMİŞ) */
    .selected-movie-card {
        background: linear-gradient(135deg, #7b33a8 0%, #9e5be0 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        color: white;
        display: flex;
        align-items: flex-start;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .selected-movie-poster {
        margin-right: 25px;
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        min-width: 150px;
        max-width: 150px;
        height: 225px;
        object-fit: cover;
        border: 2px solid #FFD700; /* Altın rengi çerçeve */
    }

    .selected-movie-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .selected-movie-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #FFD700;
        margin: 0 0 10px 0;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }

    .selected-movie-stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px 20px;
        margin-bottom: 10px;
        font-size: 1.05em;
    }

    .selected-movie-stats-grid span {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #e0e0e0;
    }

    .selected-movie-overview {
        font-size: 1em;
        line-height: 1.5;
        color: #d0d0d0;
        margin-top: 10px;
    }

    /* İstatistik Bölümü (Genel) */
    .stats-section {
        background: linear-gradient(135deg, #9c6fe8 0%, #7a4fcf 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Uygulama hakkında bölümü */
    .info-section {
        background: linear-gradient(135deg, #9c6fe8 0%, #7a4fcf 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1.2rem;
        box-shadow: 0 5px 12px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .info-section h3 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        color: #E0E0FF;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .info-section p {
        font-size: 0.9rem;
        line-height: 1.4;
        opacity: 0.95;
    }

    /* Altbilgi */
    .footer-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
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

    .no-image-placeholder {
        width: 100px;
        height: 150px;
        background: linear-gradient(135deg, #333, #555);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border-radius: 10px;
        color: #aaa;
        font-size: 0.8em;
        line-height: 1.2em;
        margin-right: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
    }

     .no-image-placeholder-large {
        width: 150px;
        height: 225px;
        background: linear-gradient(135deg, #333, #555);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border-radius: 12px;
        color: #aaa;
        font-size: 0.9em;
        line-height: 1.3em;
        margin-right: 25px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        border: 2px solid #FFD700;
    }

    /* Yükleme animasyonu */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin: 20px 0;
        font-size: 1.2em;
        font-weight: bold;
        color: #FFD700;
    }

    .loading-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        animation: loadingBounce 1.4s ease-in-out infinite both;
    }

    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    .loading-dot:nth-child(3) { animation-delay: 0s; }

    @keyframes loadingBounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }

    </style>
""", unsafe_allow_html=True)

# 🎬 Ana Başlık
st.markdown('<h1 class="main-header">🎬 Film Öneri Sistemi</h1>', unsafe_allow_html=True)

# Uygulama açıklaması
st.markdown("""
<div class="info-section">
    <h3>🎯 Gelişmiş Film Analiz Sistemi</h3>
    <p>Bu profesyonel sistem, BERT dil modelinden türetilmiş anlamsal gömme vektörleri ve gelişmiş kümeleme algoritmalarını kullanarak size en uygun film önerilerini sunar. Detaylı film bilgileri, puanlamalar, türler ve gelişmiş filtreleme seçenekleri ile sinema deneyiminizi bir üst seviyeye taşıyın.</p>
    <p>🎭 Film türlerine göre filtreleme, 🌟 IMDB puanlarına göre sıralama ve 📊 detaylı istatistikler ile keşfe başlayın!</p>
</div>
""", unsafe_allow_html=True)


# 🔁 Model dosyalarını yükle
@st.cache_resource(show_spinner="📦 Film verileri ve yapay zeka modelleri yükleniyor...")
def load_models():
    try:
        df = joblib.load("df.pkl")
        embeddings = joblib.load("embeddings.pkl")
        kmeans_model = joblib.load("kmeans_model.pkl")

        # Cluster sütunu yoksa veya boyutları uyuşmuyorsa yeniden ata
        if 'cluster' not in df.columns or len(df) != len(kmeans_model.labels_):
            st.warning(
                "Veri setinde küme etiketleri eksik veya hatalı. K-Means modeli kullanılarak yeniden oluşturuluyor.")
            df['cluster'] = kmeans_model.predict(embeddings)
        else:
            df['cluster'] = kmeans_model.labels_

        return df, embeddings, kmeans_model

    except FileNotFoundError as e:
        st.error(f"Gerekli model dosyalarından biri bulunamadı: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Model yüklenirken beklenmeyen bir hata oluştu: {e}")
        st.stop()


# Uygulama başlangıcında tüm modelleri yükle
df, combined_embeddings, kmeans_model_loaded = load_models()

# !!! GENRE COLUMNS TANIMI BURADA OLMALIDIR !!!
# DataFrame'inizdeki tür sütunlarının adlarını buraya girin
genre_columns = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
                 'Drama', 'Family', 'Fantasy', 'Foreign', 'History', 'Horror',
                 'Music', 'Mystery', 'Romance', 'Science Fiction', 'TV Movie',
                 'Thriller', 'War', 'Western']


# Veri hazırlığı ve temizleme
def prepare_data(df):
    """Veri setini analiz için hazırla"""
    df = df.copy()

    # Eksik değerleri doldur
    df['vote_average'] = df['vote_average'].fillna(0)
    df['vote_count'] = df['vote_count'].fillna(0)
    df['popularity'] = df['popularity'].fillna(0)
    df['overview'] = df['overview'].fillna("Açıklama mevcut değil")
    df['runtime'] = df['runtime'].fillna(0)
    df['revenue'] = df['revenue'].fillna(0)
    df['budget'] = df['budget'].fillna(0)

    # Türleri liste formatında hazırla (One-Hot Encoding'den liste oluşturma)
    # df.columns içinde tanımlı genre_columns sütunlarını kullanarak tür listesi oluşturulur.
    df['genres_display'] = df.apply(
        lambda row: [col for col in genre_columns if col in row.index and row[col] == 1], axis=1
    )

    # Yıl bilgisini ekle
    if 'release_year' not in df.columns and 'release_date' in df.columns:
        df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year.astype(
            'Int64')  # Int64 ile NaN'leri handle et
    elif 'release_year' not in df.columns:
        df['release_year'] = pd.NA  # Eğer release_date de yoksa

    return df


df = prepare_data(df)


# Yardımcı fonksiyonlar
def get_rating_color(rating):
    """Puana göre renk döndür"""
    if rating >= 7.5:
        return "rating-high"
    elif rating >= 6.0:
        return "rating-medium"
    else:
        return "rating-low"


def get_rating_emoji(rating):
    """Puana göre emoji döndür"""
    if rating >= 8.0:
        return "🌟"
    elif rating >= 7.0:
        return "⭐"
    elif rating >= 6.0:
        return "🔸"
    else:
        return "🔹"


def format_runtime(minutes):
    """Süreyi saat:dakika formatında döndür"""
    if pd.isna(minutes) or minutes == 0:
        return "Bilinmiyor"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if hours > 0:
        return f"{hours}s {mins}dk"
    return f"{mins}dk"


def format_budget_revenue(amount):
    """Bütçe/hasılatı formatla"""
    if pd.isna(amount) or amount == 0:
        return "Bilinmiyor"
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.1f}K"
    return f"${amount:.0f}"



# 🎛️ Filtre ve Kontrol Paneli (Geliştirilmiş Düzen - Kutu Kaldırıldı)
st.markdown('<h3 class="subheader-gradient">🎛️ Akıllı Filtre Sistemi</h3>', unsafe_allow_html=True)

# Eski filter-panel div'ini kaldırdık. Direkt kolonları ve selectbox'ları yerleştiriyoruz.
# st.markdown('<div class="filter-panel">', unsafe_allow_html=True) # Bu kaldırıldı

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<label class="filter-group-label">🎬 Film Seçin:</label>', unsafe_allow_html=True)
    valid_titles = df['title'].dropna().apply(lambda x: x.strip()).loc[lambda x: x != ""]
    
    all_movies = sorted(valid_titles.unique()) # Tüm filmlerin sıralı listesi
    
    # "The Matrix" filminin listedeki indeksini bul
    try:
        default_index = all_movies.index("The Matrix")
    except ValueError:
        default_index = 0 # Eğer "The Matrix" bulunamazsa ilk filmi seç
        
    movie_title = st.selectbox(
        "Film Seçin:",
        all_movies,
        index=default_index, # Belirlediğiniz indeksi kullan
        help="Öneri almak istediğiniz filmi seçin",
        key="movie_selector"
    )

with col2:
    st.markdown('<label class="filter-group-label">🎭 Tür Filtresi:</label>', unsafe_allow_html=True)
    # Tür filtresi
    all_genres_for_filter = [genre for genre in genre_columns if genre in df.columns]
    selected_genre = st.selectbox(
        "Tür Filtresi:",  # Bu label'ı CSS ile gizleyeceğiz
        ['Tümü'] + sorted(list(all_genres_for_filter)),
        help="Belirli bir türe odaklanın",
        key="genre_filter"  # Unique key eklendi
    )

with col3:
    st.markdown('<label class="filter-group-label">⭐ Minimum IMDB Puanı:</label>', unsafe_allow_html=True)
    # Minimum puan filtresi
    min_rating = st.selectbox(
        "Minimum IMDB Puanı:",  # Bu label'ı CSS ile gizleyeceğiz
        [0.0, 5.0, 6.0, 7.0, 8.0, 9.0],
        index=1,
        help="Sadece yüksek puanlı filmleri göster",
        key="min_rating_filter"  # Unique key eklendi
    )


# st.markdown('</div>', unsafe_allow_html=True) # Bu da kaldırıldı


# TMDb'den detaylı film bilgisi çeken fonksiyon
@st.cache_data(ttl=3600 * 24)
def get_detailed_movie_info(imdb_id):
    """TMDb'den detaylı film bilgilerini çek"""
    if not imdb_id or pd.isna(imdb_id):
        return None

    # imdb_id'yi stringe çevir ve 'tt' ile başlamasını sağla
    imdb_id_str = str(imdb_id).strip()
    if not imdb_id_str:  # Boş string kontrolü
        return None

    if not imdb_id_str.startswith("tt"):
        imdb_id_str = f"tt{imdb_id_str}"

    find_url = f"https://api.themoviedb.org/3/find/{imdb_id_str}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    try:
        response = requests.get(find_url, timeout=5)  # Timeout eklendi
        response.raise_for_status()  # HTTP hatalarını yakala (4xx veya 5xx)
        data = response.json()

        if data and data.get('movie_results'):
            movie = data['movie_results'][0]

            # Detaylı bilgi için ikinci API çağrısı
            movie_id = movie['id']
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=tr-TR"
            details_response = requests.get(details_url, timeout=5)  # Timeout eklendi
            details_response.raise_for_status()  # Hata kontrolü ekle
            details_data = details_response.json()

            # Afiş yolu
            poster_path = f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie.get('poster_path') else None
            # Daha yüksek çözünürlüklü poster (seçilen film için)
            large_poster_path = f"https://image.tmdb.org/t/p/w300{movie['poster_path']}" if movie.get(
                'poster_path') else None

            return {
                'poster_path': poster_path,
                'large_poster_path': large_poster_path,  # Yeni eklendi
                'backdrop_path': f"https://image.tmdb.org/t/p/w500{movie['backdrop_path']}" if movie.get(
                    'backdrop_path') else None,
                'tmdb_rating': details_data.get('vote_average', 0),  # Detaydan al
                'tmdb_votes': details_data.get('vote_count', 0),  # Detaydan al
                'overview': details_data.get('overview', movie.get('overview', '')),
                'genres': [g['name'] for g in details_data.get('genres', [])],
                'runtime': details_data.get('runtime', 0)
            }
        return None
    except requests.exceptions.Timeout:
        st.warning(f"TMDb API zaman aşımına uğradı. Film '{imdb_id_str}' için poster ve detaylar yüklenemedi.")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"TMDb API çağrısında hata oluştu: {e}. Film '{imdb_id_str}' için poster ve detaylar yüklenemedi.")
        return None
    except Exception as e:
        st.warning(f"Filmin TMDb bilgilerini çekerken beklenmeyen bir sorun oluştu ('{imdb_id_str}'): {e}")
        return None


# 🔍 Gelişmiş Öneri Fonksiyonu
def get_advanced_recommendations(movie_title, df, embeddings, selected_genre='Tümü', min_rating=0.0, top_n=8):
    """Gelişmiş filtreleme ile öneri yap"""
    movie_row = df[df['title'].str.lower() == movie_title.lower()]
    if movie_row.empty:
        st.warning(f"'{movie_title}' filmi veri setinde bulunamadı.")
        return []

    index = movie_row.index[0]

    if 'cluster' not in df.columns:
        st.error("Küme bilgileri DataFrame'de bulunamıyor. Lütfen model dosyalarını kontrol edin.")
        return []

    cluster_label = df.loc[index, 'cluster']

    # Filtre uygula
    filtered_df = df.copy()

    # Tür filtresi (One-Hot Encoding yapısına uygun hale getirildi)
    if selected_genre != 'Tümü':
        # Eğer seçilen tür sütunu df'de varsa ve o sütunda değeri 1 olan filmleri filtrele
        if selected_genre in df.columns:
            filtered_df = filtered_df[filtered_df[selected_genre] == 1]
        else:
            # Eğer seçilen tür sütunu df'de yoksa, bir uyarı verilebilir veya filtre uygulanmaz.
            st.warning(f"Seçilen tür '{selected_genre}' veri setinizde bir sütun olarak bulunamadı.")
            # Bu durumda tür filtresini atla, diğer filtrelerle devam et

    # Minimum puan filtresi
    filtered_df = filtered_df[filtered_df['vote_average'] >= min_rating]

    # Eğer filtrelenmiş veri çok azsa, genel benzerlik aramak için filtreyi gevşet
    if len(filtered_df) < 5:
        # Sadece puan filtresini uygula
        filtered_df = df[df['vote_average'] >= min_rating]
        if len(filtered_df) < 5:  # Hala azsa, hiç filtre uygulamadan devam et
            filtered_df = df.copy()

    if len(filtered_df) < 2:  # Çok az film kalırsa tüm veri setini kullan
        filtered_df = df.copy()

    # Aynı kümedeki filmleri bul
    cluster_movies = filtered_df[filtered_df['cluster'] == cluster_label]

    if len(cluster_movies) <= 1:
        # Küme çok küçükse veya filtreleme sonucu tek film kaldıysa, genel benzerlik ara
        movie_embedding = embeddings[index].reshape(1, -1)
        filtered_indices = filtered_df.index.tolist()
        filtered_embeddings = embeddings[filtered_indices]

        # Sadece sayısal ve sonlu (finite) değerlere sahip gömüleri kullan
        valid_indices_mask = np.all(np.isfinite(filtered_embeddings), axis=1)
        if not np.any(valid_indices_mask):  # Eğer geçerli embedding kalmadıysa
            st.warning("Filtreleme sonrası geçerli film gömüleri bulunamadı. Popüler filmler gösteriliyor.")
            return df.sort_values(by='popularity', ascending=False).head(top_n).to_dict('records')

        filtered_indices = np.array(filtered_indices)[valid_indices_mask].tolist()
        filtered_embeddings = filtered_embeddings[valid_indices_mask]

        if not filtered_embeddings.shape[0] > 0:  # filtered_embeddings boşsa
            return df.sort_values(by='popularity', ascending=False).head(top_n).to_dict('records')

        similarities = cosine_similarity(movie_embedding, filtered_embeddings)[0]

        similarity_df = pd.DataFrame({
            'index': filtered_indices,
            'similarity': similarities
        }).query('index != @index').sort_values(by='similarity', ascending=False).head(top_n)

        recommendations = []
        for _, row in similarity_df.iterrows():
            movie_data = df.loc[row['index']].to_dict()
            movie_data['similarity_score'] = row['similarity']
            recommendations.append(movie_data)

        return recommendations

    # Küme içinde benzerlik hesapla
    cluster_indices = cluster_movies.index.tolist()
    movie_embedding = embeddings[index].reshape(1, -1)
    cluster_embeddings = embeddings[cluster_indices]

    # Sadece sayısal ve sonlu (finite) değerlere sahip gömüleri kullan
    valid_cluster_indices_mask = np.all(np.isfinite(cluster_embeddings), axis=1)
    if not np.any(valid_cluster_indices_mask):
        st.warning("Küme içinde geçerli film gömüleri bulunamadı. Genel benzerlik aranıyor.")
        return get_advanced_recommendations(movie_title, df, embeddings, selected_genre, min_rating,
                                            top_n)  # Rekürsif çağrı

    cluster_indices = np.array(cluster_indices)[valid_cluster_indices_mask].tolist()
    cluster_embeddings = cluster_embeddings[valid_cluster_indices_mask]

    if not cluster_embeddings.shape[0] > 0:
        return df.sort_values(by='popularity', ascending=False).head(top_n).to_dict('records')

    similarities = cosine_similarity(movie_embedding, cluster_embeddings)[0]

    similarity_df = pd.DataFrame({
        'index': cluster_indices,
        'similarity': similarities
    }).query('index != @index').sort_values(by='similarity', ascending=False).head(top_n)

    recommendations = []
    for _, row in similarity_df.iterrows():
        movie_data = df.loc[row['index']].to_dict()
        movie_data['similarity_score'] = row['similarity']
        recommendations.append(movie_data)

    return recommendations


# 🚀 Gelişmiş Öneri Butonu
if st.button("🎥 Akıllı Öneri Sistemi - Analiz Et", disabled=(movie_title is None), use_container_width=True):
    if movie_title:
        # Yükleme animasyonu ve mesajı
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div class="loading-animation">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <span>Filmler analiz ediliyor... Bu biraz zaman alabilir.</span>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(f"🎬 '{movie_title}' filmine benzer öneriler bulunuyor..."):
            start_time = time.time()
            recommendations = get_advanced_recommendations(
                movie_title, df, combined_embeddings,
                selected_genre, min_rating, top_n=8
            )
            end_time = time.time()

        loading_placeholder.empty()  # Yükleme animasyonunu kaldır

        if recommendations:
            # Seçilen filmin detayları
            selected_movie = df[df['title'].str.lower() == movie_title.lower()].iloc[0]
            selected_movie_tmdb_info = get_detailed_movie_info(selected_movie.get('imdb_id'))

            selected_movie_poster_html = ""
            if selected_movie_tmdb_info and selected_movie_tmdb_info['large_poster_path']:
                selected_movie_poster_html = f'<img src="{selected_movie_tmdb_info["large_poster_path"]}" class="selected-movie-poster" alt="Poster">'
            else:
                selected_movie_poster_html = '<div class="no-image-placeholder-large">Afiş Mevcut Değil</div>'

            # TMDb'den gelen özet ve türleri tercih et
            selected_overview_display = selected_movie_tmdb_info.get('overview', selected_movie.get('overview',
                                                                                                    'Açıklama mevcut değil')) if selected_movie_tmdb_info else selected_movie.get(
                'overview', 'Açıklama mevcut değil')
            selected_genres_to_display = selected_movie_tmdb_info.get('genres', selected_movie.get('genres_display',
                                                                                                   [])) if selected_movie_tmdb_info else selected_movie.get(
                'genres_display', [])
            selected_runtime_display = format_runtime(
                selected_movie_tmdb_info['runtime']) if selected_movie_tmdb_info and selected_movie_tmdb_info.get(
                'runtime', 0) > 0 else format_runtime(selected_movie['runtime'])

            st.markdown(f"""
            <div class="selected-movie-card">
                {selected_movie_poster_html}
                <div class="selected-movie-info">
                    <h3 class="selected-movie-title">🎯 Seçilen Film: {selected_movie['title']} ({int(selected_movie['release_year']) if not pd.isna(selected_movie['release_year']) else 'Bilinmiyor'})</h3>
                    <div class="selected-movie-stats-grid">
                        <span class="{get_rating_color(selected_movie['vote_average'])}">
                            {get_rating_emoji(selected_movie['vote_average'])} <b>IMDB Puanı:</b> {selected_movie['vote_average']:.1f}/10
                        </span>
                        <span>🗳️ <b>Oy Sayısı:</b> {selected_movie['vote_count']:,.0f}</span>
                        <span>⏱️ <b>Süre:</b> {selected_runtime_display}</span>
                    </div>
                    <p><b>🎭 Türler:</b> {', '.join(selected_genres_to_display) if selected_genres_to_display else 'Bilinmiyor'}</p>
                    <p class="selected-movie-overview"><b>Özet:</b> {selected_overview_display}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<h3>🔍 <u>{movie_title}</u> filmine benzer {len(recommendations)} öneri:</h3>",
                        unsafe_allow_html=True)

            for i, movie_data in enumerate(recommendations, 1):
                # TMDb'den detaylı bilgi al
                tmdb_info = get_detailed_movie_info(movie_data.get('imdb_id'))

                # Film kartı oluştur
                poster_html = ""
                if tmdb_info and tmdb_info['poster_path']:
                    poster_html = f'<img src="{tmdb_info["poster_path"]}" class="movie-poster" alt="Poster">'
                else:
                    poster_html = '<div class="no-image-placeholder">Poster Mevcut Değil</div>'

                # IMDB puanını ve oy sayısını kullan (öncelikli olarak kendi verimizden)
                imdb_rating = movie_data.get('vote_average', 0)
                imdb_votes = movie_data.get('vote_count', 0)
                runtime_display = format_runtime(movie_data.get('runtime', 0))
                release_year = int(movie_data['release_year']) if not pd.isna(
                    movie_data['release_year']) else 'Bilinmiyor'

                # TMDB'den gelen detayları (özellikle özet ve türler) tercih et
                overview_display = tmdb_info.get('overview', movie_data.get('overview',
                                                                            'Açıklama mevcut değil')) if tmdb_info else movie_data.get(
                    'overview', 'Açıklama mevcut değil')
                genres_to_display = tmdb_info.get('genres', movie_data.get('genres_display',
                                                                           [])) if tmdb_info else movie_data.get(
                    'genres_display', [])

                # Eğer TMDB runtime boşsa kendi verimizden kullan
                if tmdb_info and tmdb_info.get('runtime', 0) > 0:
                    runtime_display = format_runtime(tmdb_info['runtime'])

                st.markdown(f"""
                <div class="movie-card">
                    {poster_html}
                    <div class="movie-info">
                        <h4 class="movie-title">{i}. {movie_data['title']} ({release_year})</h4>
                        <div class="movie-genres">
                            {''.join([f'<span class="genre-tag">{g}</span>' for g in genres_to_display])}
                        </div>
                        <div class="movie-stats">
                            <span class="stat-item {get_rating_color(imdb_rating)}">
                                {get_rating_emoji(imdb_rating)} <b>IMDB:</b> {imdb_rating:.1f}/10
                            </span>
                            <span class="stat-item">
                                🗳️ <b>Oylar:</b> {imdb_votes:,.0f}
                            </span>
                            <span class="stat-item">
                                ⏱️ <b>Süre:</b> {runtime_display}
                            </span>
                        </div>
                        <p class="movie-overview"><b>Özet:</b> {overview_display}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(
                f"Üzgünüz, '{movie_title}' için öneri bulunamadı. Lütfen başka bir film deneyin veya filtreleri değiştirin. (Çok kısıtlı filtreler seçmiş olabilirsiniz)")
    else:
        st.info(
            "Lütfen öneri almak için yukarıdan bir film seçin ve 'Akıllı Öneri Sistemi - Analiz Et' butonuna tıklayın.")

st.divider()  # --- yerine Streamlit'in kendi divider'ını kullanmak daha temiz


# 📚 Proje Hakkında
st.markdown("""
<div class="footer-section">
    <h3>💡 Film Öneri Sistemi</h3>
    <p>Bu Akıllı Film Öneri Sistemi, yapay zeka ve veri bilimi tekniklerinin güçlü birleşimiyle oluşturulmuştur.</p>
    <p><b>Geliştirici:</b> S.S. 🚀 | <b>Sürüm:</b> 1.0.0 | <b>Son Güncelleme:</b> Haziran 2025</p>
</div>
""", unsafe_allow_html=True)
