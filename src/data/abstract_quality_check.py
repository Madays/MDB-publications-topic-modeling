#from lexicalrichness import LexicalRichness

#Lexical Richness (Vocabulary Diversity)
#lex = LexicalRichness(abstract)
#lex.mtld # Higher = more diverse


#Presence of Key Content Words


import re
import spacy
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from lexical_diversity import lex_div as ld
from sentence_transformers import SentenceTransformer, util
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="lexical_diversity.lex_div")
nltk.download('punkt')

sample_path = "../../data/interim/stratified_sample.csv"
interim_dir = "data/interim"
output_path = os.path.join(interim_dir, "quality_abstracts.csv")
# NLP setup
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")  # Small and fast

def sentence_coherence_score(text):
    doc = list(nlp(text).sents)
    sentences = [sent.text.strip() for sent in doc if len(sent) > 3]
    if len(sentences) < 2:
        return 0
    embeddings = semantic_model.encode(sentences, convert_to_tensor=True)
    cosine_sim_matrix = util.pytorch_cos_sim(embeddings, embeddings).numpy()
    upper_triangle = cosine_sim_matrix[np.triu_indices_from(cosine_sim_matrix, k=1)]
    return np.mean(upper_triangle)

def is_valid_abstract(
    text,
    ttr_threshold=0.4,
    mtld_threshold=20,
    stopword_threshold=0.6,
    min_sentences=2,
    min_coherence=0.5,
    check_semantics=False
):
    if not isinstance(text, str):
        return False

    text = text.strip()
    if text.lower() in ["n/a", "abstract not available", "not available"]:
        return False

    # Length
    if len(text) < 300:
        return False

    # Stopword ratio
    words = word_tokenize(text.lower())
    if not words:
        return False
    stopword_ratio = sum(1 for w in words if w in stop_words) / len(words)
    if stopword_ratio >= stopword_threshold:
        return False

    # Lexical diversity
    ttr = len(set(words)) / len(words)
    mtld = ld.mtld(words)
    if ttr < ttr_threshold and mtld < mtld_threshold:
        return False

    # POS + Named entities
    doc = nlp(text)
    pos_tags = {token.pos_ for token in doc}
    if not {"NOUN", "VERB"}.issubset(pos_tags):
        return False
    if not any(ent.label_ for ent in doc.ents):
        return False

    # Syntactic structure
    num_sents = len(list(doc.sents))
    avg_sent_len = len(doc) / num_sents if num_sents else 0
    if num_sents < min_sentences or not (5 < avg_sent_len < 40):
        return False

    # Semantic coherence (optional)
    if check_semantics:
        coherence = sentence_coherence_score(text)
        if coherence < min_coherence:
            return False

    return True



df = pd.read_csv('C:/Users/amali/Documents/AI Study Group/maday/MDB-publications-topic-modeling/data/interim/stratified_sample.csv')  # or from API result
print(df)
df["is_valid"] = df["abstract"].apply(lambda x: is_valid_abstract(x, check_semantics=True))
filtered_df = df[df["is_valid"] == True]


# Save result
filtered_df.to_csv(output_path, index=False)
print(f"Dataframe with abstract quality check done: {output_path}")