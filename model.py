# =========================================================
# MOVIE RECOMMENDATION & POPULARITY PREDICTION SYSTEM
# =========================================================

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
import ast
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings('ignore')

# =========================================================
# 1. DATA LOADING & EDA (CLO 1)
# =========================================================
print("Loading Dataset...")
df = pd.read_csv('movies_metadata.csv').head(25000) # Optimized for i5 8th Gen

# Basic EDA
print("\nDataset Info:")
print(df.info())
print("\nMissing Values:")
print(df.isnull().sum())

# Visualizing Target Distribution
df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0)
df['target'] = df['vote_average'].apply(lambda x: 1 if x >= 7.0 else 0)

plt.figure(figsize=(6,4))
sns.countplot(x='target', data=df, palette='viridis')
plt.title("EDA: Popular (1) vs Non-Popular (0) Movies")
plt.show()

# =========================================================
# 2. PREPROCESSING & CLEANING (CLO 1)
# =========================================================
df = df[['title', 'overview', 'genres', 'tagline', 'target']].dropna(subset=['title'])
df['overview'] = df['overview'].fillna('')
df['tagline'] = df['tagline'].fillna('')

def convert_genres(obj):
    try: return " ".join([i['name'] for i in ast.literal_eval(obj)])
    except: return ""

df['genres'] = df['genres'].apply(convert_genres)
df['tags'] = (df['overview'] + " " + df['genres'] + " " + df['tagline']).str.lower()

# Text Cleaning (Lemmatization)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = re.sub(r'[^a-z\s]', '', text)
    return " ".join([lemmatizer.lemmatize(w) for w in text.split() if w not in stop_words])

print("Preprocessing Tags...")
df['tags'] = df['tags'].apply(clean_text)

# Feature Encoding (TF-IDF)
tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
X = tfidf.fit_transform(df['tags']) # Sparse Matrix for RAM optimization
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# =========================================================
# 3. MODEL DEVELOPMENT & EVALUATION (CLO 5)
# =========================================================

def evaluate_model(model, name, color):
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    pre = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"{name} Results -> Acc: {acc:.2f}, Pre: {pre:.2f}, Rec: {rec:.2f}, F1: {f1:.2f}")
    
    # Confusion Matrix Graph
    plt.figure(figsize=(4,3))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap=color)
    plt.title(f"{name} Confusion Matrix")
    plt.show()
    
    return [acc, pre, rec, f1]

# Implementing Models
results = {}
results['Random Forest'] = evaluate_model(RandomForestClassifier(n_estimators=100, n_jobs=-1), "Random Forest", "Blues")
results['Gradient Boosting'] = evaluate_model(GradientBoostingClassifier(n_estimators=100), "Gradient Boosting", "Greens")
results['AdaBoost'] = evaluate_model(AdaBoostClassifier(n_estimators=100), "AdaBoost", "Oranges")

# Voting & Stacking
print("\nTraining Ensemble Methods (Voting/Stacking)...")
rf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
gb = GradientBoostingClassifier(n_estimators=100)
ada = AdaBoostClassifier(n_estimators=100)

voting = VotingClassifier(estimators=[('rf', rf), ('gb', gb), ('ada', ada)], voting='hard', n_jobs=-1)
results['Voting'] = evaluate_model(voting, "Voting Classifier", "Purples")

stacking = StackingClassifier(estimators=[('rf', rf), ('gb', gb), ('ada', ada)], final_estimator=LogisticRegression(), n_jobs=-1)
results['Stacking'] = evaluate_model(stacking, "Stacking Classifier", "Reds")

# =========================================================
# 4. FINAL COMPARISON
# =========================================================
res_df = pd.DataFrame(results, index=['Accuracy', 'Precision', 'Recall', 'F1-Score']).T
print("\nFinal Comparison Table:")
print(res_df)

res_df.plot(kind='bar', figsize=(10,6))
plt.title("Model Performance Comparison")
plt.ylabel("Score")
plt.xticks(rotation=15)
plt.show()

# =========================================================
# 5. MOVIE RECOMMENDATION (FINAL STEP)
# =========================================================
print("\nBuilding Recommendation System...")
similarity = cosine_similarity(X)

def recommend(movie):
    try:
        idx = df[df['title'].str.contains(movie, case=False)].index[0]
        distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])[1:11]
        print(f"\nRecommended Movies for '{df.iloc[idx].title}':")
        for i in distances:
            print(f"- {df.iloc[i[0]].title}")
    except:
        print("Movie not found in current processed set.")

recommend("Batman")
recommend("Inception")
recommend("The Godfather")
recommend("Nonexistent Movie")
recommend("Avengers")
recommend("Toy Story")
recommend("Pulp Fiction")