# model.py - Düzeltilmiş ve İyileştirilmiş Versiyon
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import Ridge
from sklearn.ensemble import StackingRegressor
from catboost import CatBoostRegressor
import pandas as pd
import joblib


def get_model_features(df, target='vote_average'):
    """Model için özellikleri hazırlar"""
    # Hariç tutulacak sütunlar (model için gereksiz)
    excluded_columns = [
        'id', 'title', 'overview', 'original_language', 'production_companies',
        'production_countries', 'spoken_languages', 'status', 'cleaned_title',
        'cleaned_countries', 'grouped_countries', 'release_date', 'imdb_id',
        'tagline', 'homepage', 'adult'  # Ek gereksiz sütunlar
    ]

    # Özellikleri seç
    features = df.drop(columns=excluded_columns, errors='ignore')

    # Sadece sayısal sütunları al
    features = features.select_dtypes(include=['number', 'bool'])

    # Hedef değişkeni ayır
    if target in features.columns:
        X = features.drop(columns=[target])
        y = features[target]

        # Sonsuz değerleri temizle
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())

        # Hedef değişkenindeki sonsuz/NaN değerleri temizle
        mask = np.isfinite(y) & y.notna()
        X = X[mask]
        y = y[mask]

    else:
        raise ValueError(f"Hedef değişken '{target}' DataFrame'de bulunamadı!")

    print(f"Model eğitimi için {X.shape[1]} özellik ve {X.shape[0]} örnek kullanılacak.")
    print(f"Hedef değişken istatistikleri:")
    print(f"  - Min: {y.min():.2f}")
    print(f"  - Max: {y.max():.2f}")
    print(f"  - Ortalama: {y.mean():.2f}")
    print(f"  - Standart sapma: {y.std():.2f}")

    return X, y


def train_catboost_model(df, target='vote_average', save_model=True):
    """CatBoost modelini eğitir"""
    X, y = get_model_features(df, target)

    # Veri bölme
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )

    print(f"Eğitim seti boyutu: {X_train.shape}")
    print(f"Test seti boyutu: {X_test.shape}")

    # CatBoost modeli
    model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.1,
        depth=8,
        eval_metric='RMSE',
        random_seed=42,
        verbose=100,
        early_stopping_rounds=100,
        l2_leaf_reg=3,
        bagging_temperature=1
    )

    # Model eğitimi
    model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        use_best_model=True,
        plot=False
    )

    # Tahmin ve değerlendirme
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Eğitim seti metrikleri
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    train_r2 = r2_score(y_train, y_pred_train)
    train_mae = mean_absolute_error(y_train, y_pred_train)

    # Test seti metrikleri
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_r2 = r2_score(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)

    print("\n=== MODEL PERFORMANSI ===")
    print(f"Eğitim Seti - RMSE: {train_rmse:.4f}, R²: {train_r2:.4f}, MAE: {train_mae:.4f}")
    print(f"Test Seti - RMSE: {test_rmse:.4f}, R²: {test_r2:.4f}, MAE: {test_mae:.4f}")

    # Overfitting kontrolü
    if train_r2 - test_r2 > 0.1:
        print("⚠️  UYARI: Model overfitting gösteriyor olabilir!")

    # Özellik önem sıralaması
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\n=== EN ÖNEMLİ 10 ÖZELLİK ===")
    print(feature_importance.head(10))

    # Model ve scaler'ı kaydet
    if save_model:
        joblib.dump(model, 'catboost_model.pkl')
        joblib.dump(X.columns.tolist(), 'feature_columns.pkl')
        print("\nModel 'catboost_model.pkl' olarak kaydedildi.")
        print("Özellik sütunları 'feature_columns.pkl' olarak kaydedildi.")

    return model, test_rmse, test_r2


def predict_movie_rating(model, feature_columns, movie_data):
    """Yeni bir film için rating tahmini yapar"""
    try:
        # Girdi verisini DataFrame'e dönüştür
        if isinstance(movie_data, dict):
            input_df = pd.DataFrame([movie_data])
        else:
            input_df = movie_data.copy()

        # Eksik sütunları 0 ile doldur
        for col in feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0

        # Sadece model özelliklerini al
        input_df = input_df[feature_columns]

        # Sonsuz değerleri temizle
        input_df = input_df.replace([np.inf, -np.inf], 0)
        input_df = input_df.fillna(0)

        # Tahmin yap
        prediction = model.predict(input_df)

        # Rating'i 0-10 arasında sınırla
        prediction = np.clip(prediction, 0, 10)

        return prediction[0] if len(prediction) == 1 else prediction

    except Exception as e:
        print(f"Tahmin hatası: {e}")
        return None


def load_model_and_predict(movie_data):
    """Kaydedilmiş modeli yükler ve tahmin yapar"""
    try:
        model = joblib.load('catboost_model.pkl')
        feature_columns = joblib.load('feature_columns.pkl')

        prediction = predict_movie_rating(model, feature_columns, movie_data)
        return prediction

    except FileNotFoundError:
        print("Model dosyası bulunamadı! Önce modeli eğitip kaydedin.")
        return None
    except Exception as e:
        print(f"Model yükleme hatası: {e}")
        return None