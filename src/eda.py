# Veri ön işleme
# Eksik değer, analiz ve görselleştirme
#Bu dosyada temel metin temizleme ve TF-IDF işlemlerini fonksiyon haline getiriyoruz.

import pandas as pd
import re
import string
from matplotlib import pyplot as plt
import seaborn as sns


def visualize_missing_values(df):
    missing_counts = df.isnull().sum()
    missing_ratio = (missing_counts / len(df)) * 100
    missing_df = pd.DataFrame({'Eksik Sayısı': missing_counts, 'Eksik Oran (%)': missing_ratio})
    missing_df = missing_df[missing_df['Eksik Sayısı'] > 0].sort_values(by='Eksik Oran (%)', ascending=False)

    print(missing_df)

    plt.figure(figsize=(10, 8))
    sns.barplot(x=missing_df['Eksik Oran (%)'], y=missing_df.index, palette='viridis')
    plt.title('Eksik Değer Oranları')
    plt.xlabel('Eksik Oran (%)')
    plt.ylabel('Özellik')
    plt.tight_layout()
    plt.show()
    return df



# TF-IDF vektörleştirme fonksiyonu
def get_tfidf_matrix(text_series, max_features=1000):
    cleaned_texts = text_series.apply(clean_text)
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    return tfidf_df

"""
plt.rcParams['font.family'] = 'Arial'  # veya 'sans-serif', 'SimHei' gibi fontlar deneyebilirsin
importances = model.feature_importances_
feature_names = X.columns  # modele verilen tüm öznitelikler
matplotlib.use('TkAgg')  # veya 'Qt5Agg' deneyebilirsin

# Görselleştirme
plt.figure(figsize=(12, 8))
plt.barh(feature_names, importances)
plt.title("Özellik Önem Grafiği", fontsize=14)
plt.xlabel("Önem Derecesi", fontsize=12)
plt.ylabel("Özellikler", fontsize=12)
plt.tight_layout()
plt.show(block=True)"""