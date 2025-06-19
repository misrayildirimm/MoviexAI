# pre.py - Düzeltilmiş ve İyileştirilmiş Versiyon
import pandas as pd
import numpy as np
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt


def fill_missing_values(df):
    """Eksik değerleri doldurma fonksiyonu"""
    # original_language
    if 'original_language' in df.columns:
        most_common_lang = df['original_language'].mode()[0]
        df['original_language'] = df['original_language'].fillna(most_common_lang)

    # popularity
    if 'popularity' in df.columns:
        df['popularity'] = df['popularity'].fillna(df['popularity'].median())

    # release_date → datetime dönüşüm ve median ile doldurma
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        # NaN olmayan değerlerde, integer timestamp'e çevir, medyanı al
        median_timestamp = df['release_date'].dropna().astype(np.int64).median()
        median_date = pd.to_datetime(median_timestamp)
        df['release_date'] = df['release_date'].fillna(median_date)

    # release_year, month, day
    if 'release_year' in df.columns:
        df['release_year'] = df['release_year'].fillna(df['release_year'].median())
    if 'release_month' in df.columns:
        df['release_month'] = df['release_month'].fillna(df['release_month'].median())
    if 'release_day' in df.columns:
        df['release_day'] = df['release_day'].fillna(df['release_day'].median())

    # runtime
    if 'runtime' in df.columns:
        df['runtime'] = df['runtime'].fillna(df['runtime'].median())

    # spoken_languages
    if 'spoken_languages' in df.columns:
        df['spoken_languages'] = df['spoken_languages'].fillna('unknown')

    return df


def clean_text(text):
    """Metin verisini temizle"""
    if pd.isna(text):
        return ""
    text = str(text).lower()  # String'e dönüştür ve küçük harfe çevir
    text = re.sub(r'\d+', '', text)  # Sayıları sil
    text = text.translate(str.maketrans('', '', string.punctuation))  # Noktalama temizle
    text = text.strip()
    return text


def preprocess_overview_column(df):
    """'overview' sütununu temizler ve TF-IDF matrisine dönüştürür"""
    # overview'ı boş string ile değiştir ve temizleme fonksiyonunu uygula
    df["overview"] = df["overview"].fillna("").apply(clean_text)

    # TF-IDF vektörleştirici nesnesini tanımla
    tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

    # 'overview' sütununu TF-IDF matrisine dönüştür
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["overview"])

    return df, tfidf_matrix, tfidf_vectorizer


def preprocess_genres_column(df):
    """Genres sütununu işleyerek liste formatına dönüştürür"""
    print("Her film için tür listeleri oluşturuluyor...")
    df["genre_list"] = df["genres"].fillna("").apply(
        lambda x: [g.strip() for g in x.split("|")] if x else []
    )

    print(f"Toplam {len(df)} film için tür listesi işlendi.")
    return df


def convert_popularity_to_numeric(df):
    """Popularity sütununu sayısal tipe dönüştürür"""
    if 'popularity' in df.columns:
        print(f"'popularity' sütununun mevcut veri tipi: {df['popularity'].dtype}")
        if df['popularity'].dtype == 'object':
            print("'popularity' sütunu sayısal tipe dönüştürülüyor...")
            df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
            print(f"'popularity' sütununun yeni veri tipi: {df['popularity'].dtype}")
    return df


def encode_genres_one_hot(df):
    """Genres için One-Hot Encoding"""
    print("Türler için One-Hot Encoding başlatılıyor...")

    if 'genre_list' not in df.columns:
        print("HATA: 'genre_list' sütunu bulunamadı!")
        return df

    # MultiLabelBinarizer'ı başlat
    mlb = MultiLabelBinarizer()

    # One-Hot Encode et
    encoded_genres = mlb.fit_transform(df['genre_list'])

    # DataFrame'e dönüştür
    genre_df = pd.DataFrame(encoded_genres, columns=mlb.classes_, index=df.index)

    print(f"Toplam {len(mlb.classes_)} adet benzersiz tür tespit edildi.")

    # Orijinal sütunları kaldır
    df = df.drop(columns=['genres', 'genre_list'], errors='ignore')

    # One-Hot encoded sütunları ekle
    df = pd.concat([df, genre_df], axis=1)

    print("One-Hot Encoding tamamlandı.")
    return df


def preprocess_title_column(df):
    """Title sütununu temizler ve TF-IDF'e dönüştürür"""
    print("Başlık sütunu ön işleme başlatılıyor...")

    if 'title' not in df.columns:
        print("HATA: 'title' sütunu bulunamadı!")
        return df, None, None

    # Eksik değerleri doldur
    df['title'].fillna('', inplace=True)

    # Temizle
    df['cleaned_title'] = df['title'].apply(clean_text)

    # TF-IDF
    title_tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=2000)
    title_tfidf_matrix = title_tfidf_vectorizer.fit_transform(df['cleaned_title'])

    print(f"Başlıklar için TF-IDF matrisi şekli: {title_tfidf_matrix.shape}")
    return df, title_tfidf_matrix, title_tfidf_vectorizer


def drop_imdb_id_column(df):
    """IMDB ID sütununu siler"""
    if 'imdb_id' in df.columns:
        df = df.drop(columns=['imdb_id'])
        print("'imdb_id' sütunu silindi.")
    return df


def drop_tagline_column(df):
    """Tagline sütununu siler"""
    if 'tagline' in df.columns:
        df = df.drop(columns=['tagline'])
        print("'tagline' sütunu silindi.")
    return df


def clean_and_encode_production_countries(df, top_n=10, prefix='country', drop_columns=True):
    """Production countries için temizleme ve encoding"""
    if drop_columns:
        df.drop(columns=['cleaned_countries', 'grouped_countries'], inplace=True, errors='ignore')

    # Standardizasyon haritası
    standard_map = {
        "united states of america": "usa",
        "america": "usa",
        "us": "usa",
        "usa": "usa",
        "united kingdom": "uk",
        "great britain": "uk",
        "britain": "uk",
        "soviet union": "russia",
        "russian federation": "russia",
        "republic of korea": "south korea",
        "korea, south": "south korea",
        "korea, north": "north korea",
        "czech republic": "czechia",
        "czechoslovakia": "czechia",
        "serbia and montenegro": "serbia"
    }

    def clean_country(cell):
        if pd.isna(cell):
            return np.nan
        c = str(cell).strip().lower()
        return standard_map.get(c, c)

    # Temizle
    if 'production_countries' in df.columns:
        df['cleaned_countries'] = df['production_countries'].apply(clean_country)

        # En iyi N ülkeleri bul
        top_countries = df['cleaned_countries'].value_counts().nlargest(top_n).index

        # Diğerlerini 'others' olarak grupla
        df['grouped_countries'] = df['cleaned_countries'].apply(
            lambda x: x if x in top_countries else 'others'
        )

        # One-hot encoding
        one_hot_df = pd.get_dummies(df['grouped_countries'], prefix=prefix)
        df = pd.concat([df, one_hot_df], axis=1)

        print(f"En iyi {top_n} ülke + diğerleri için one-hot encoding yapıldı.")

    return df


def clean_status_column(df):
    """Status sütununu temizler"""
    if 'status' in df.columns:
        df['status'] = df['status'].fillna('Unknown')
        df['status'] = df['status'].apply(
            lambda x: 'Unknown' if isinstance(x, str) and x.strip() == '' else x
        )
    return df


def process_release_date(df):
    """Release date sütununu işler"""
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_year'] = df['release_date'].dt.year
        df['release_month'] = df['release_date'].dt.month
        df['release_day'] = df['release_date'].dt.day
    return df


def top_n_one_hot_encode(df, column_name, top_n=10, prefix='encoded'):
    """En sık geçen top_n değeri one-hot encode eder"""
    if column_name not in df.columns:
        print(f"UYARI: '{column_name}' sütunu bulunamadı!")
        return df, []

    # En çok geçen top_n değeri bul
    top_values = df[column_name].value_counts().nlargest(top_n).index

    # Diğerlerini 'Others' olarak grupla
    grouped_col = df[column_name].apply(lambda x: x if x in top_values else 'Others')

    # One-hot encoding
    df_encoded = pd.get_dummies(grouped_col, prefix=prefix)

    # DataFrame ile birleştir
    df = pd.concat([df, df_encoded], axis=1)

    return df, df_encoded.columns.tolist()


def top_n_one_hot_encode_language(df, column='original_language', top_n=10, prefix='lang'):
    """Dil sütunu için one-hot encoding"""
    if column not in df.columns:
        print(f"UYARI: '{column}' sütunu bulunamadı!")
        return df

    top_values = df[column].value_counts().nlargest(top_n)
    print(f"\nEn çok kullanılan {top_n} dil:")
    for lang, count in top_values.items():
        print(f"{lang}: {count} adet")

    top_languages = top_values.index
    df[f'{column}_grouped'] = df[column].apply(
        lambda x: x if x in top_languages else 'other'
    )

    one_hot = pd.get_dummies(df[f'{column}_grouped'], prefix=prefix)
    df = pd.concat([df, one_hot], axis=1)
    df.drop(columns=[f'{column}_grouped'], inplace=True)

    return df


def drop_and_print_columns(df, column_to_drop='original_title'):
    """Belirtilen sütunu siler ve kalan sütunları yazdırır"""
    if column_to_drop in df.columns:
        df = df.drop(columns=[column_to_drop])
        print(f"'{column_to_drop}' sütunu silindi.")
    else:
        print(f"'{column_to_drop}' sütunu zaten yok.")

    print(f"Kalan sütun sayısı: {df.shape[1]}")
    return df


def remove_outliers_iqr(df, columns):
    """IQR yöntemi ile aykırı değerleri temizler"""
    for col in columns:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            original_size = df.shape[0]
            df = df[(df[col] >= lower) & (df[col] <= upper)]
            removed = original_size - df.shape[0]
            print(f"{col} sütununda {removed} aykırı değer temizlendi.")

    return df


def create_new_features(df):
    """Yeni özellikler türetir"""
    current_year = 2025

    if 'release_year' in df.columns:
        df['movie_age'] = current_year - df['release_year']

    if 'budget' in df.columns and 'revenue' in df.columns:
        df['return_ratio'] = df.apply(
            lambda row: row['revenue'] / row['budget'] if row['budget'] > 0 else 0,
            axis=1
        )

    return df


def plot_correlation_heatmap(df):
    """Korelasyon heatmap'i çizer"""
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()

    plt.figure(figsize=(15, 12))
    sns.heatmap(corr, cmap='coolwarm', annot=False, center=0)
    plt.title("Korelasyon Matrisi")
    plt.tight_layout()
    plt.show()

    return df