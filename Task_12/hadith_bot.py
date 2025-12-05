import glob
import re
import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer
import faiss

# 1. Setup Paths
# Changed from '/content/LK-Hadith-Corpus' to local path
REPO_PATH = 'LK-Hadith-Corpus'

print("Looking for CSV files...")
files = sorted(glob.glob(os.path.join(REPO_PATH, '**', '*.csv'), recursive=True))
print(f"Found {len(files)} CSV files.")

# 2. Clean Text Function
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text) # remove punctuations
    text = re.sub(r'\s+', ' ', text)           # removes extra space
    return text

# 3. Load Data
# Corrected columns based on actual CSV structure
columns = [
    'Chapter_Number', 'Chapter_English', 'Chapter_Arabic',
    'Section_Number', 'Section_English', 'Section_Arabic',
    'Hadith_Number',
    'English_Hadith', 'English_Isnad', 'English_Matn',
    'Arabic_Hadith', 'Arabic_Isnad', 'Arabic_Matn', 'Arabic_Comment',
    'English_Grade', 'Arabic_Grade'
]

all_hadith = []

print("Processing files...")
for file in files:
    try:
        # Use the corrected columns list for reading
        df = pd.read_csv(file, names=columns, skiprows=1, on_bad_lines='skip')
        
        df['Cleaned_Hadith'] = df['English_Hadith'].astype(str).apply(clean_text)
        
        all_hadith.extend(df.values.tolist())
    except Exception as e:
        print(f"Error reading {file}: {e}")

print(f"Total Hadiths loaded: {len(all_hadith)}")

# Re-create columns list with Cleaned_Hadith for DataFrame creation
df_columns = columns + ['Cleaned_Hadith']
hadith_df = pd.DataFrame(all_hadith, columns=df_columns)
# hadith_df.to_csv('cleaned_hadith_data.csv', index=False) # Optional

# 4. Embeddings
print("Loading Sentence Transformer Model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

EMBEDDINGS_FILE = 'hadith_embeddings.npy'

if os.path.exists(EMBEDDINGS_FILE):
    print("Loading existing embeddings...")
    embeddings = np.load(EMBEDDINGS_FILE)
else:
    print("Generating embeddings (this may take time)...")
    # Process in batches to show progress or avoid OOM if huge (though 34k is fine)
    embeddings = model.encode(hadith_df['Cleaned_Hadith'].values, show_progress_bar=True)
    np.save(EMBEDDINGS_FILE, embeddings)

embeddings = np.array(embeddings)

# 5. FAISS Index
print("Building FAISS Index...")
dimensions = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimensions)
faiss_index.add(embeddings)
faiss.write_index(faiss_index, "faiss_index.index")

# 6. Search Function
def get_similar_hadith(query, count=5):
    print(f"\nQuery: {query}")
    query_embedding = model.encode([query])
    distance, indices = faiss_index.search(query_embedding, count)

    results = []
    for i in range(count):
        idx = indices[0][i]
        dist = distance[0][i]
        hadith_text = hadith_df['English_Hadith'].iloc[idx]
        # Handle potential float/nan values in text fields
        chapter = str(hadith_df['Chapter_English'].iloc[idx])
        section = str(hadith_df['Section_English'].iloc[idx])
        source = f"Chapter: {chapter}, Section: {section}"
        
        results.append({
            'hadith': hadith_text,
            'distance': float(dist),
            'source': source,
            'arabic_hadith': str(hadith_df['Arabic_Hadith'].iloc[idx]),
            'grade': str(hadith_df['English_Grade'].iloc[idx])
        })
        
    return results

# 7. Test
if __name__ == "__main__":
    results = get_similar_hadith("How many prayers are there?")
    for r in results:
        print(f"Hadith: {r['hadith']}")
        print("-" * 80)
