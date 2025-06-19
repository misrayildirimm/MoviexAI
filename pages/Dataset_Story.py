import ast
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import plotly.express as px
import numpy as np

# set_page_config() her Streamlit dosyasında (sayfasında)
# SADECE BİR KEZ ve İLK STREAMLIT KOMUTU olarak çağrılmalıdır.
# Bu, sayfa başlığını, ikonunu ve düzenini ayarlar.
st.set_page_config(page_title="📊 Veri Seti Hikayesi", layout="wide", page_icon="📊")

# 🌈 Özel stil - IMDB Rating Tahmin Uygulamasındaki ana başlık gradyanı entegre edildi
st.markdown("""
    <style>
    /* Genel Streamlit arka plan rengini koyu temaya uygun olarak ayarla */
    body {
        background-color: #000000; /* Tamamen siyah arka plan */
        color: #e0e0e0; /* Açık gri metin rengi */
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
        -webkit-text-fill-color: transparent; /* Burası tekrar transparent yapıldı! */
        margin-bottom: 2rem;
        animation: gradientShift 4s ease-in-out infinite;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        display: flex; /* İçindeki öğeleri hizalamak için flexbox kullan */
        justify-content: center; /* Yatayda ortala */
        align-items: center; /* Dikeyde ortala */
    }

    /* Ana başlık ikonunun stili - görünür olması için ayrı renk verildi */
    .main-header .icon {
        -webkit-text-fill-color: initial; /* Bu span içindeki metnin şeffaflığını kaldırır */
        color: #bb6aee; /* İkona belirgin bir renk ver (altın sarısı iyi gidecektir) */
        margin-right: 10px; /* Metinle arasında boşluk bırak */
        font-size: 1.1em; /* İkonu biraz büyüt */
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Bilgi bölümleri için kart stili */
    .info-section, .data-summary-card, .viz-card { /* .viz-card sınıfı da buraya eklendi */
        background: linear-gradient(135deg, #9c6fe8 0%, #7a4fcf 100%); /* Mor gradyan tekrar eklendi */
        padding: 15px 25px; /* Padding azaltıldı */
        margin-bottom: 20px; /* Alt boşluk azaltıldı */
        border-radius: 10px; /* Köşe yuvarlama azaltıldı */
        box-shadow: 0 4px 10px rgba(0,0,0,0.2); /* Gölge azaltıldı */
        color: white;
        border: 1px solid rgba(255,255,255,0.1); /* Kenarlık inceltildi */
    }
    .info-section h3, .data-summary-card h3, .viz-card h3 { /* .viz-card başlığı da eklendi */
        font-size: 1.5rem; /* Başlık boyutu küçültüldü */
        margin-bottom: 0.8rem; /* Alt boşluk azaltıldı */
        color: white; /* BAŞLIK BEYAZ YAPILDI */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2); /* Gölge azaltıldı */
    }
    .info-section p, .data-summary-card p, .viz-card p { /* .viz-card paragrafı da eklendi */
        font-size: 0.95rem; /* Paragraf metin boyutu küçültüldü */
        line-height: 1.5; /* Satır yüksekliği ayarlandı */
        opacity: 0.95;
    }

    /* Yeni kompakt özellik tablosu ve kutu stilleri */
    .feature-category-card {
        background-color: #1a1a1a; /* Daha koyu gri arka plan (siyaha daha yakın) */
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px; /* Kategoriler arası boşluk */
        box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        border: 1px solid #3a3a3a; /* Kenarlık rengi siyaha uygun */
        height: 100%; /* Column içinde eşit yükseklik */
    }
    .feature-category-card h4 {
        color: #bb6aee; /* Altın sarısı başlık */
        font-size: 1.25rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .feature-category-card h4 svg { /* Icon stili */
        margin-right: 8px;
        fill: #bb6aee; /* Icon rengi */
    }
    .feature-item {
        margin-bottom: 8px;
        font-size: 0.95rem;
        color: #e0e0e0;
        line-height: 1.4;
    }
    .feature-item strong {
        color: #FFF; /* Özellik adı daha belirgin */
    }
    .feature-item span {
        opacity: 0.85; /* Açıklama hafif şeffaf */
    }

    /* Altbilgi (main app'deki ile aynı) */
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


# Veri setini yükle (st.cache_data kullanılarak performans artırılabilir)
@st.cache_data
def load_data():
    try:
        df_loaded = pd.read_csv("data/AllMoviesDetailsCleaned.csv", sep=';', low_memory=False)
        return df_loaded
    except FileNotFoundError:
        st.error("Veri dosyası 'data/raw/AllMoviesDetailsCleaned.csv' bulunamadı. Lütfen dosya yolunu kontrol edin.")
        st.stop()
    except Exception as e:
        st.error(f"Veri yüklenirken bir hata oluştu: {e}")
        st.stop()


df = load_data()

# --- Veri Temizliği ve Ön İşleme (Görselleştirmeler için kritik) ---
# Tarih sütununu doğru formata çevir ve yıl/ay/gün çıkar
if 'release_date' in df.columns:
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    df['release_month'] = df['release_date'].dt.month
    df['release_day'] = df['release_date'].dt.day

# budget ve revenue sütunlarındaki 0 veya NaN değerleri filtrele
initial_rows = len(df)
df_filtered_finance = df[(df['budget'].notna()) & (df['revenue'].notna()) &
                         (df['budget'] > 0) & (df['revenue'] > 0)].copy()

# 'popularity' ve 'revenue' sütunlarını float'a dönüştürme
for col in ['popularity', 'revenue', 'budget']:
    if col in df_filtered_finance.columns:
        df_filtered_finance[col] = pd.to_numeric(
            df_filtered_finance[col].astype(str).str.replace(',', '.', regex=False).replace('nan', np.nan),
            errors='coerce'
        )
        # NaN değerleri filtrele
        df_filtered_finance = df_filtered_finance[df_filtered_finance[col].notna()]

st.sidebar.info(
    f"Orijinal {initial_rows} filmden, analiz ve görselleştirme için {len(df_filtered_finance)} film kullanılıyor (Bütçe ve Hasılat sıfır/boş olmayanlar ve geçerli finansal değerler).")

# 🎬 Ana Başlık - İkonun ayrı span'de olduğu ve renk aldığı kısım
st.markdown('<h1 class="main-header"><span class="icon">📊</span> Veri Seti Hikayesi</h1>', unsafe_allow_html=True)

# Proje Özeti ve Giriş
st.markdown("""
<div class="info-section">
    <h3>🎯 Proje Özeti</h3>
    <p>Bu sayfa, <b>Akıllı Film Öneri Sistemi Projesi</b>'nin temelini oluşturan veri setimizi derinlemesine inceliyor. Amacımız, mevcut verilere dayanarak filmlerin kullanıcı puanlarını tahmin etmek ve kişiselleştirilmiş film önerileri sunmaktır.</p>
    <p>Film endüstrisi ve izleyiciler için daha doğru değerlendirme sistemleri geliştirmeyi ve kullanıcı deneyimini iyileştirmeyi hedefliyoruz.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Projenin Hikayesi (daha özet)
st.markdown("""
<div class="data-summary-card">
    <h3>💡 Projenin Hikayesi ve Yaklaşımımız</h3>
    <p>Mevcut film öneri sistemlerinin yetersizliğini gözlemleyerek yola çıktık. Amacımız, geleneksel yaklaşımlar yerine, filmlerin türleri, IMBD puanları, yapımcı bilgileri ve teknik detaylar gibi içeriksel faktörleri derinlemesine analiz eden, daha kişiselleştirilmiş bir öneri sistemi geliştirmektir.</p>
    <p>Bu proje, hem denetimli (rating tahmini) hem de denetimsiz (öneri sistemi) makine öğrenimi tekniklerini kullanarak film severlere daha isabetli ve zengin bir film keşif deneyimi sunmayı hedeflemektedir.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Veri Seti Değişkenleri (Yeni, iki sütunlu ve kategorize edilmiş stil)
st.header("🔍 Veri Setimizdeki Temel Sütunlar")
st.markdown("""
    <p style="font-size:1.05rem; text-align: center; color: #e0e0e0; margin-bottom: 25px;">
    Veri setimiz, filmlerin çeşitli özelliklerini içeren <b>37 sütundan</b> oluşmaktadır. Bu sütunlar, analiz ve modelleme süreçlerimiz için kritik öneme sahiptir. Aşağıda, ana kategoriler altında bu sütunların açıklamalarını bulabilirsiniz:
    </p>
""", unsafe_allow_html=True)

# Streamlit'in columns özelliğini kullanarak iki sütunlu düzen oluşturma
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-category-card">
        <h4><svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="css-i6dzq1"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM12 10v4M12 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"></path></svg> Tanımlayıcı Bilgiler</h4>
        <div class="feature-item"><strong>id:</strong> <span>Her film için benzersiz tanımlayıcı numara.</span></div>
        <div class="feature-item"><strong>imdb_id:</strong> <span>IMDB veritabanındaki benzersiz film kimliği.</span></div>
        <div class="feature-item"><strong>original_title:</strong> <span>Filmin orijinal adı.</span></div>
        <div class="feature-item"><strong>title:</strong> <span>Yayınlanan film adı.</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-category-card">
        <h4>🧑‍🎨 İçerik Bilgileri</h4>
        <div class="feature-item"><strong>genres:</strong> <span>Filmin türleri (aksiyon, drama vb.). Liste formatında.</span></div>
        <div class="feature-item"><strong>overview:</strong> <span>Filmin kısa özeti veya açıklaması.</span></div>
        <div class="feature-item"><strong>tagline:</strong> <span>Filmin sloganı.</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-category-card">
        <h4>🏢 Yapımcı ve Stüdyo Bilgileri</h4>
        <div class="feature-item"><strong>production_companies:</strong> <span>Filmde yer alan yapım şirketleri (liste formatında).</span></div>
        <div class="feature-item"><strong>production_companies_number:</strong> <span>Yapımcı şirket sayısı.</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-category-card">
        <h4>🧪 Film Özellikleri (İçeriksel/Fiziksel)</h4>
        <div class="feature-item"><strong>status:</strong> <span>Filmin yayın durumu (Released, Post Production vb.).</span></div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-category-card">
        <h4>💰 Finansal Bilgiler</h4>
        <div class="feature-item"><strong>budget:</strong> <span>Filmin yapım bütçesi (USD cinsinden).</span></div>
        <div class="feature-item"><strong>revenue:</strong> <span>Filmin elde ettiği toplam gelir (USD cinsinden).</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-category-card">
        <h4>🌍 Dil ve Ülke Bilgileri</h4>
        <div class="feature-item"><strong>original_language:</strong> <span>Filmin orijinal dili (örn: en, fr, tr).</span></div>
        <div class="feature-item"><strong>spoken_languages:</strong> <span>Filmde konuşulan diller (liste formatında).</span></div>
        <div class="feature-item"><strong>spoken_languages_number:</strong> <span>Filmde konuşulan dil sayısı.</span></div>
        <div class="feature-item"><strong>production_countries:</strong> <span>Yapımın gerçekleştiği ülkeler (liste formatında).</span></div>
        <div class="feature-item"><strong>production_countries_number:</strong> <span>Yapım ülkesi sayısı.</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-category-card">
        <h4>⏰ Zaman Bilgileri</h4>
        <div class="feature-item"><strong>runtime:</strong> <span>Filmin süresi (dakika).</span></div>
        <div class="feature-item"><strong>release_date:</strong> <span>Filmin vizyon tarihi.</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-category-card">
        <h4>🌟 İzleyici ve Değerlendirme Bilgileri</h4>
        <div class="feature-item"><strong>vote_average:</strong> <span>Kullanıcı oylaması ortalaması.</span></div>
        <div class="feature-item"><strong>vote_count:</strong> <span>Oylama sayısı (kaç kişi oy vermiş).</span></div>
        <div class="feature-item"><strong>popularity:</strong> <span>TMDB tarafından hesaplanan popülerlik skoru.</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Veri Keşfi: Sayısal Sütunların Dağılımı
st.header("📊 Veri Keşfi: Sayısal Sütunların Dağılımı ve Korelasyonları")

st.markdown("""
<div class="data-summary-card">
    <h3>📈 Sayısal Sütunların Dağılımı</h3>
    <p>Veri setimizdeki sayısal sütunların dağılımını görselleştirerek, veri yapımızı daha iyi anlamayı ve olası aykırı değerleri veya eğilimleri keşfetmeyi hedefliyoruz.</p>
</div>
""", unsafe_allow_html=True)

numerical_cols = ['budget', 'revenue', 'popularity', 'vote_average', 'runtime', 'vote_count',
                  'production_companies_number', 'production_countries_number', 'spoken_languages_number']
numeric_df = df_filtered_finance[numerical_cols].select_dtypes(include=['number'])

if not numeric_df.empty:
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 15))
    axes = axes.flatten()
    for i, col in enumerate(numeric_df.columns):
        if i < len(axes):
            sns.histplot(numeric_df[col].dropna(), kde=True, ax=axes[i], color='#bb6aee')
            axes[i].set_title(f'{col} Dağılımı', color='#e0e0e0', fontsize=12)
            axes[i].set_xlabel("")
            axes[i].set_ylabel("")
            axes[i].tick_params(axis='x', colors='#e0e0e0', labelsize=9)
            axes[i].tick_params(axis='y', colors='#e0e0e0', labelsize=9)
            axes[i].set_facecolor('#282836')
            plt.setp(axes[i].spines.values(), color='#4a4a60')
            plt.setp([axes[i].get_xticklines(), axes[i].get_yticklines()], color='#4a4a60')
    plt.tight_layout()
    fig.patch.set_facecolor('#1a1a2e')
    st.pyplot(fig)
else:
    st.warning("Görselleştirilecek sayısal sütun bulunamadı veya finansal filtreleme sonrası boş.")

# --- İkili Grafik Düzeni Başlangıcı ---
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💰 Bütçe vs Hasılat İlişkisi")
    st.markdown("""
    <div class="viz-card">
        <p>Filmlerin bütçesi ile gişe hasılatı arasındaki ilişkiyi gösterir. Genellikle, yüksek bütçe yüksek hasılatla ilişkilidir.</p>
    </div>
    """, unsafe_allow_html=True)

    if not df_filtered_finance.empty:
        correlation = df_filtered_finance['budget'].corr(df_filtered_finance['revenue'])
        joint_fig = sns.jointplot(data=df_filtered_finance, x="budget", y="revenue", kind="scatter", alpha=0.5,
                                  color='#bb6aee', height=5)
        joint_fig.fig.suptitle(f"Bütçe vs Hasılat (Korelasyon: {correlation:.2f})", y=1.02,
                               color='#e0e0e0', fontsize=14)
        joint_fig.set_axis_labels("Bütçe (USD)", "Hasılat (USD)", color='#e0e0e0')

        joint_fig.ax_joint.set_facecolor('#282836')
        joint_fig.ax_marg_x.set_facecolor('#282836')
        joint_fig.ax_marg_y.set_facecolor('#282836')
        joint_fig.fig.set_facecolor('#1a1a2e')

        joint_fig.ax_joint.tick_params(axis='x', colors='#e0e0e0', labelsize=9)
        joint_fig.ax_joint.tick_params(axis='y', colors='#e0e0e0', labelsize=9)
        joint_fig.ax_marg_x.tick_params(axis='x', colors='#e0e0e0', labelsize=9)
        joint_fig.ax_marg_y.tick_params(axis='y', colors='#e0e0e0', labelsize=9)

        plt.setp(joint_fig.ax_joint.spines.values(), color='#4a4a60')
        plt.setp(joint_fig.ax_marg_x.spines.values(), color='#4a4a60')
        plt.setp(joint_fig.ax_marg_y.spines.values(), color='#4a4a60')

        st.pyplot(joint_fig)
    else:
        st.warning("Bütçe-Hasılat grafiği için yeterli veri yok.")

with col_right:
    st.subheader("⭐ Popülerlik vs Hasılat İlişkisi")
    st.markdown("""
    <div class="viz-card">
        <p>Filmlerin popülerliği ile gişe hasılatı arasındaki ilişkiyi inceler. Popülerlik arttıkça hasılatın da arttığı gözlemlenir.</p>
    </div>
    """, unsafe_allow_html=True)

    if not df_filtered_finance.empty:
        correlation_pop_rev = df_filtered_finance['popularity'].corr(df_filtered_finance['revenue'])
        joint_fig_pop_rev = sns.jointplot(data=df_filtered_finance, x='popularity', y='revenue', kind='scatter',
                                          alpha=0.5,
                                          color='#D8BFD8', height=5)
        joint_fig_pop_rev.fig.suptitle(f"Popülerlik vs Hasılat (Korelasyon: {correlation_pop_rev:.2f})",
                                       y=1.02, color='#e0e0e0', fontsize=14)
        joint_fig_pop_rev.set_axis_labels("Popülerlik Skoru", "Hasılat (USD)", color='#e0e0e0')

        joint_fig_pop_rev.ax_joint.set_facecolor('#282836')
        joint_fig_pop_rev.ax_marg_x.set_facecolor('#282836')
        joint_fig_pop_rev.ax_marg_y.set_facecolor('#282836')
        joint_fig_pop_rev.fig.set_facecolor('#1a1a2e')

        joint_fig_pop_rev.ax_joint.tick_params(axis='x', colors='#e0e0e0', labelsize=9)
        joint_fig_pop_rev.ax_joint.tick_params(axis='y', colors='#e0e0e0', labelsize=9)
        joint_fig_pop_rev.ax_marg_x.tick_params(axis='x', colors='#e0e0e0', labelsize=9)
        joint_fig_pop_rev.ax_marg_y.tick_params(axis='y', colors='#e0e0e0', labelsize=9)

        plt.setp(joint_fig_pop_rev.ax_joint.spines.values(), color='#4a4a60')
        plt.setp(joint_fig_pop_rev.ax_marg_x.spines.values(), color='#4a4a60')
        plt.setp(joint_fig_pop_rev.ax_marg_y.spines.values(), color='#4a4a60')

        st.pyplot(joint_fig_pop_rev)
    else:
        st.warning("Popülerlik-Hasılat grafiği için yeterli veri yok.")

# --- İkili Grafik Düzeni Devamı ---
st.markdown("---")
col_left_2, col_right_2 = st.columns(2)

numerical_cols_for_corr = ['budget', 'revenue', 'popularity', 'vote_average', 'runtime', 'vote_count',
                           'production_companies_number', 'production_countries_number', 'spoken_languages_number']
numeric_corr_df = df_filtered_finance[numerical_cols_for_corr].select_dtypes(include=['number'])

with col_left_2:
    st.subheader("🔥 Korelasyon Heatmap")
    st.markdown("""
    <div class="viz-card">
        <p>Sayısal değişkenler arasındaki ilişkileri gösterir ve modelleme için önemli ipuçları sunar.</p>
    </div>
    """, unsafe_allow_html=True)

    if not numeric_corr_df.empty and len(numeric_corr_df.columns) > 1:
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(numeric_corr_df.corr(), annot=True, cmap="YlOrRd", fmt=".2f", linewidths=".5", ax=ax_corr,
                    cbar_kws={'label': 'Korelasyon Katsayısı'})
        ax_corr.set_title("Sayısal Değişkenler Arası Korelasyon", color='#e0e0e0', fontsize=14)
        ax_corr.tick_params(axis='x', colors='#e0e0e0', labelsize=9)
        ax_corr.tick_params(axis='y', colors='#e0e0e0', labelsize=9)
        ax_corr.set_facecolor('#282836')
        fig_corr.patch.set_facecolor('#1a1a2e')
        st.pyplot(fig_corr)
    else:
        st.warning("Korelasyon heatmap'i için yeterli sayısal sütun bulunamadı.")

with col_right_2:
    st.subheader("🌐 Filmlerin Orijinal Diline Göre Dağılım")
    st.markdown("""
    <div class="viz-card">
        <p>Veri setindeki filmlerin orijinal dillerine göre yüzdesel dağılımını gösterir.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'original_language' not in df.columns or df['original_language'].isnull().all():
        st.warning("Orijinal dil verisi bulunamadı veya 'original_language' sütunu boş.")
    else:
        language_map = {
            'en': 'İngilizce', 'fr': 'Fransızca', 'es': 'İspanyolca', 'de': 'Almanca', 'ja': 'Japonca',
            'zh': 'Çince', 'ko': 'Korece', 'it': 'İtalyanca', 'ru': 'Rusça', 'hi': 'Hintçe',
            'ar': 'Arapça', 'cn': 'Kantonca', 'pt': 'Portekizce', 'da': 'Danca', 'sv': 'İsveççe',
            'no': 'Norveççe', 'nl': 'Flemenkçe', 'fi': 'Fince', 'pl': 'Lehçe', 'th': 'Tayca',
            'tr': 'Türkçe', 'cs': 'Çekçe', 'hu': 'Macarca', 'id': 'Endonezce', 'fa': 'Farsça',
            'el': 'Yunanca', 'he': 'İbranice', 'ro': 'Rumence', 'ta': 'Tamilce', 'te': 'Telugu Dili'
        }
        language_counts = df['original_language'].value_counts().reset_index()
        language_counts.columns = ['Language_Code', 'Count']
        language_counts['Language'] = language_counts['Language_Code'].map(language_map).fillna(
            language_counts['Language_Code'])

        threshold_percentage = 1.0
        total_films_language = language_counts['Count'].sum()
        language_counts['Percentage'] = (language_counts['Count'] / total_films_language) * 100
        other_languages_df = language_counts[language_counts['Percentage'] < threshold_percentage]
        main_languages_df = language_counts[language_counts['Percentage'] >= threshold_percentage]

        if not other_languages_df.empty:
            other_count = other_languages_df['Count'].sum()
            other_percentage = other_languages_df['Percentage'].sum()
            main_languages_df = pd.concat([main_languages_df, pd.DataFrame([['Diğer', other_count, other_percentage]],
                                                                           columns=['Language_Code', 'Count',
                                                                                    'Percentage'])], ignore_index=True)
            main_languages_df.loc[main_languages_df['Language_Code'] == 'Diğer', 'Language'] = 'Diğer'

        main_languages_df = main_languages_df.sort_values(by='Percentage', ascending=False)

        if main_languages_df.empty:
            st.warning("Pasta grafiği için yeterli dil verisi bulunamadı.")
        else:
            fig_pie_lang = px.pie(main_languages_df,
                                  values='Count',
                                  names='Language',
                                  title='Filmlerin Orijinal Diline Göre Dağılımı',
                                  hole=0.3,
                                  color_discrete_sequence=px.colors.sequential.Plasma_r,
                                  template="plotly_dark",
                                  height=400)

            fig_pie_lang.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie_lang.update_layout(title_font_color='#e0e0e0', title_font_size=16)
            st.plotly_chart(fig_pie_lang, use_container_width=True)

# --- Üçüncü İkili Grafik Düzeni ---
st.markdown("---")
col_left_3, col_right_3 = st.columns(2)

with col_left_3:
    st.subheader("🏆 En Yüksek Puanlı Filmler (İlk 20)")
    st.markdown("""
    <div class="viz-card">
        <p>Belirli oy sayısının üzerinde, izleyiciler tarafından en çok beğenilen filmleri gösterir.</p>
    </div>
    """, unsafe_allow_html=True)

    top_movies = df[df['vote_count'] > 50].sort_values(by=['vote_average', 'vote_count'],
                                                       ascending=[False, False]).head(20)

    if not top_movies.empty:
        fig_top_movies = px.bar(top_movies, x='title', y='vote_average',
                                title='En Yüksek Puanlı Filmler (En Az 50 Oy)',
                                labels={'title': 'Film Adı', 'vote_average': 'Ortalama Puan'},
                                hover_data=['vote_count', 'release_year'],
                                color='vote_average',
                                color_continuous_scale=px.colors.sequential.Plasma,
                                template="plotly_dark",
                                height=450)
        fig_top_movies.update_layout(xaxis={'categoryorder': 'total descending'},
                                     title_font_color='#e0e0e0', title_font_size=16,
                                     xaxis_tickfont_size=10, yaxis_tickfont_size=10)
        st.plotly_chart(fig_top_movies, use_container_width=True)
    else:
        st.warning("En yüksek puanlı filmler bulunamadı veya yetersiz veri var.")

with col_right_3:
    st.subheader("📅 Yıllara Göre Film Üretimi")
    st.markdown("""
    <div class="viz-card">
        <p>Film endüstrisindeki yıllara göre üretim trendlerini gösterir.</p>
    </div>
    """, unsafe_allow_html=True)

    movies_per_year = df['release_year'].dropna()
    movies_per_year = movies_per_year[movies_per_year > 0].astype(int).value_counts().sort_index().reset_index()
    movies_per_year.columns = ['Year', 'Count']

    if not movies_per_year.empty:
        fig_years = px.line(movies_per_year, x='Year', y='Count',
                            title='Yıllara Göre Film Üretimi Trendi',
                            labels={'Year': 'Yıl', 'Count': 'Film Sayısı'},
                            markers=True,
                            template="plotly_dark",
                            color_discrete_sequence=[px.colors.sequential.RdPu[5]],
                            height=450)
        fig_years.update_layout(title_font_color='#e0e0e0', title_font_size=16,
                                xaxis_tickfont_size=10, yaxis_tickfont_size=10)
        st.plotly_chart(fig_years, use_container_width=True)
    else:
        st.warning("Yıl verileri bulunamadı veya işlenemedi.")

# --- Dördüncü İkili Grafik Düzeni ---
st.markdown("---")
col_left_4, col_right_4 = st.columns(2)

with col_left_4:
    st.subheader("💲 Orijinal Dili İngilizce Olan/Olmayanların Ortalama Geliri")
    st.markdown("""
    <div class="viz-card">
        <p>Filmlerin orijinal dilinin (İngilizce veya Diğer) ortalama gelir üzerindeki etkisini gösterir. İngilizce filmlerin genellikle daha yüksek gişe başarısı elde ettiği gözlemlenir.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'original_language' not in df_filtered_finance.columns or df_filtered_finance.empty:
        st.warning("Grafik oluşturmak için 'original_language' sütunu bulunamadı veya DataFrame boş.")
    elif 'revenue' not in df_filtered_finance.columns:
        st.warning("Grafik oluşturmak için 'revenue' sütunu bulunamadı.")
    else:
        # 'is_english' sütununu oluştur
        df_filtered_finance['is_english_group'] = df_filtered_finance['original_language'].apply(
            lambda x: 'İngilizce' if x == 'en' else 'Diğer Diller'
        )

        # Her grubun ortalama (veya medyan) gelirini hesapla
        # Medyanı tercih edebiliriz, çünkü gelir dağılımı genellikle çarpıktır.
        # Burada ortalama kullanılmıştır. Medyan için .mean() yerine .median() kullanın.
        average_revenue_by_language = df_filtered_finance.groupby('is_english_group')['revenue'].mean().reset_index()
        average_revenue_by_language.columns = ['Dil Grubu', 'Ortalama Gelir']

        if average_revenue_by_language.empty or average_revenue_by_language['Ortalama Gelir'].sum() == 0:
            st.warning(
                "Ortalama gelir grafiği oluşturmak için yeterli veri bulunamadı. Lütfen 'revenue' ve 'original_language' sütunlarındaki verileri kontrol edin.")
        else:
            fig_avg_revenue = px.bar(average_revenue_by_language,
                                     x='Dil Grubu',
                                     y='Ortalama Gelir',
                                     title='Orijinal Dili İngilizce Olan/Olmayan Filmlerin Ortalama Geliri',
                                     labels={'Dil Grubu': 'Orijinal Dil', 'Ortalama Gelir': 'Ortalama Gelir (USD)'},
                                     color='Dil Grubu',
                                     color_discrete_map={'İngilizce': '#bb6aee', 'Diğer Diller': '#D8BFD8'},
                                     template="plotly_dark",
                                     height=450)

            fig_avg_revenue.update_layout(title_font_color='#e0e0e0', title_font_size=16,
                                          xaxis_tickfont_size=12, yaxis_tickfont_size=10,
                                          yaxis_tickformat=".2s")  # Gelir değerlerini daha okunaklı formatla (örn: 10M, 100K)
            fig_avg_revenue.update_xaxes(title_font_color='#e0e0e0')
            fig_avg_revenue.update_yaxes(title_font_color='#e0e0e0')
            st.plotly_chart(fig_avg_revenue, use_container_width=True)

with col_right_4:
    st.subheader("🎬 Film Türlerinin Ortalama IMDB Puanlarına Etkisi")
    st.markdown("""
    <div class="viz-card">
        <p>Her bir film türünün ortalama IMDB puanlarını karşılaştırarak, hangi türlerin genel olarak daha yüksek değerlendirildiğini gösterir.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'genres' not in df.columns or 'vote_average' not in df.columns:
        st.warning("Grafik oluşturmak için 'genres' veya 'vote_average' sütunu bulunamadı.")
    else:
        # Sadece gerekli sütunları içeren ve NaN değerleri olmayan bir kopya oluşturalım
        df_genres = df[(df['genres'].notna()) & (df['vote_average'].notna()) & (df['vote_count'].notna())].copy()

        # `vote_count` için eşik değerini daha esnek yapalım.
        # Örneğin, en az 5 oy almış filmleri dahil edelim.
        df_genres = df_genres[df_genres['vote_count'] > 5]  # Eşiği 10'dan 5'e düşürdük


        # `genres` sütununu işleme fonksiyonu
        def parse_genres_robust(genres_str):
            if pd.isna(genres_str) or not isinstance(genres_str, str):
                return []

            # JSON formatını dene
            try:
                genres_list = ast.literal_eval(genres_str)
                if isinstance(genres_list, list):
                    return [g['name'] for g in genres_list if isinstance(g, dict) and 'name' in g]
            except (ValueError, SyntaxError):
                pass  # JSON formatı değilse devam et

            # Pipe ile ayrılmış string formatını dene (örn: 'Action|Drama')
            try:
                return [g.strip() for g in genres_str.split('|') if g.strip()]
            except:
                pass  # Diğer hataları yoksay

            return []  # Hiçbiri uymazsa boş liste döndür


        df_genres['parsed_genres'] = df_genres['genres'].apply(parse_genres_robust)

        # Boş liste olan satırları filtrele
        df_exploded_genres = df_genres[df_genres['parsed_genres'].apply(lambda x: len(x) > 0)].explode('parsed_genres')

        # Gerekli kontrolleri tekrar yapalım
        if df_exploded_genres.empty:
            st.warning(
                "Film türlerinin ortalama IMDB puanları grafiği için yeterli veri bulunamadı. Lütfen veri setinizdeki 'genres', 'vote_average' ve 'vote_count' sütunlarını kontrol edin.")
        else:
            # Her tür için ortalama IMDB puanını hesapla
            genre_avg_score = df_exploded_genres.groupby('parsed_genres')['vote_average'].mean().reset_index()
            genre_avg_score.columns = ['Genre', 'Average_IMDB_Score']

            # Sadece belirli bir sayıda filmi olan türleri alalım (örn: en az 20 film)
            # Bu, az sayıda filmi olan türlerin puanlarını yanıltıcı olmaktan kurtarır.
            genre_counts = df_exploded_genres['parsed_genres'].value_counts().reset_index()
            genre_counts.columns = ['Genre', 'Count']

            # Puanları hesaplanan türler ile film sayısı olan türleri birleştir
            genre_avg_score = pd.merge(genre_avg_score, genre_counts, on='Genre')

            # Minimum film sayısına göre filtrele (örn: 20 filmden az olan türleri at)
            min_films_for_genre = 20  # Bu değeri değiştirebilirsiniz
            genre_avg_score = genre_avg_score[genre_avg_score['Count'] >= min_films_for_genre]

            genre_avg_score = genre_avg_score.sort_values(by='Average_IMDB_Score', ascending=False)

            if genre_avg_score.empty:
                st.warning(
                    f"Ortalama IMDB puanı hesaplanacak yeterli film (en az {min_films_for_genre} filmlik tür) bulunamadı. Lütfen filtreleme koşullarını veya veri setini kontrol edin.")
            else:
                fig_genres_score = px.bar(genre_avg_score, x='Genre', y='Average_IMDB_Score',
                                          title=f'Film Türlerinin Ortalama IMDB Puanları (En Az {min_films_for_genre} Filmlik Türler)',
                                          labels={'Genre': 'Film Türü', 'Average_IMDB_Score': 'Ortalama IMDB Puanı'},
                                          hover_data=['Count'],
                                          color='Average_IMDB_Score',
                                          color_continuous_scale=px.colors.sequential.Viridis,
                                          template="plotly_dark",
                                          height=450)

                fig_genres_score.update_layout(xaxis={'categoryorder': 'total descending'},
                                               title_font_color='#e0e0e0', title_font_size=16,
                                               xaxis_tickfont_size=9, yaxis_tickfont_size=10)
                fig_genres_score.update_xaxes(tickangle=45)

                st.plotly_chart(fig_genres_score, use_container_width=True)

# --- Alt Bilgi ---
st.markdown("---")
st.markdown("""
<div class="footer-section">
    <p>Bu analiz, film verilerini anlamanıza ve keşfetmenize yardımcı olmak için hazırlanmıştır.</p>
    <p>📧 İletişim: info@filmanalytics.com | 🌐 Website: www.filmanalytics.com</p>
</div>
""", unsafe_allow_html=True)