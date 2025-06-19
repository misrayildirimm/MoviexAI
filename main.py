# Ana çalışma dosyası
import pandas as pd
import numpy as np
import joblib
# Gerekli ön işleme fonksiyonlarını 'src/preprocessing' modülünden içe aktarır.
from src.eda import visualize_missing_values
from sklearn.preprocessing import StandardScaler
from models import train_catboost_model
from src.preprocessing import (
    preprocess_overview_column,
    preprocess_genres_column,
    convert_popularity_to_numeric,
    encode_genres_one_hot,
    preprocess_title_column,
    drop_imdb_id_column,
    clean_and_encode_production_countries,
    drop_tagline_column,
    clean_status_column,
    process_release_date,
    top_n_one_hot_encode,
    top_n_one_hot_encode_language,
    drop_and_print_columns
)
import warnings
warnings.filterwarnings('ignore')

# Veri okuma ve df adlı kopya üzerinden işlemleri başlatma.
df_ = pd.read_csv('data/AllMoviesDetailsCleaned.csv', sep=";", low_memory=False)  #low_memory=False büyük dosyalar için veri türlerini doğru anlamaya yardımcı olur.
df = df_.copy()

# Ana dosyada fonksiyonları çağırır. Dönen değişkenleri sol taraftaki dataframe'e atar.
df, tfidf_matrix, tfidf_vectorizer = preprocess_overview_column(df)
df = preprocess_genres_column(df)
df = convert_popularity_to_numeric(df)
df, title_tfidf_matrix, title_tfidf_vectorizer = preprocess_title_column(df)
df = encode_genres_one_hot(df)
df = drop_imdb_id_column(df)
df = drop_tagline_column(df)
df = clean_and_encode_production_countries(df, top_n=10)
df = clean_status_column(df)
df = process_release_date(df)
df, company_cols = top_n_one_hot_encode(df, 'production_companies', top_n=10, prefix='company')
df, language_cols = top_n_one_hot_encode(df, 'spoken_languages', top_n=10, prefix='language')
df = top_n_one_hot_encode_language(df, column='original_language', top_n=10, prefix='lang')
df = drop_and_print_columns(df, column_to_drop='original_title')
#df = visualize_missing_values(df)
df = fill_missing_values(df)  #eksik değerleri doldurdu

numerical_cols = [
        'budget', 'popularity', 'revenue', 'runtime', 'vote_count',
        'release_year', 'release_month', 'release_day'
]
numerical_cols = [col for col in numerical_cols if col in df.columns]
print(f"Sayısal sütunlar: {numerical_cols}")

# 16. Aykırı değerleri temizle
print("\n15. Aykırı değerler temizleniyor...")
original_size = df.shape[0]
df = remove_outliers_iqr(df.copy(), numerical_cols)
print(f"Aykırı değer temizleme sonrası: {original_size} -> {df.shape[0]} satır")

# 17. Sonsuz değerleri temizle
print("\n16. Sonsuz değerler temizleniyor...")
df = df.replace([np.inf, -np.inf], np.nan)

# 1. Log dönüşüm
print("\n18. Logaritmik dönüşümler yapılıyor...")
log_cols = ['budget', 'revenue', 'popularity', 'vote_count']
for col in log_cols:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: np.log1p(x) if pd.notnull(x) and x >= 0 else x)

#Ek binary özellikler (has_budget, has_revenue, vs.)
df["has_budget"] = df["budget"].apply(lambda x: 1 if x > 0 else 0)
df["has_revenue"] = df["revenue"].apply(lambda x: 1 if x > 0 else 0)
df["has_votes"] = df["vote_count"].apply(lambda x: 1 if x > 0 else 0)
# 2. Özellik mühendisliği (logtan önce de olabilir ama sonra olması daha anlamlı olabilir)
df = create_new_features(df)



X, y = get_model_features(df, target='vote_average')  # veya 'vote_count'
catboost_model = train_catboost_model(df)


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
print(df.head())
print(df.isnull().sum())
print(df.describe())
print(df.info())


