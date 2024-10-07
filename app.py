from flask import Flask, request, render_template
import os
import re
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Function Definitions (from BIM model)
def preprocess(text):
    return re.findall(r'\b\w+\b', text.lower())

def load_documents(folder_path):
    docs = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                docs[filename] = preprocess(file.read())
    return docs

def compute_statistics(docs):
    doc_count = len(docs)
    term_doc_freq = defaultdict(int)
    term_freq = defaultdict(lambda: defaultdict(int))

    for doc_id, words in docs.items():
        word_set = set(words)
        for word in words:
            term_freq[doc_id][word] += 1
        for word in word_set:
            term_doc_freq[word] += 1

    return term_freq, term_doc_freq, doc_count

def compute_relevance_prob(query, term_freq, term_doc_freq, doc_count):
    scores = {}
    for doc_id in term_freq:
        score = 1.0
        for term in query:
            tf = term_freq[doc_id].get(term, 0)
            df = term_doc_freq.get(term, 0)
            p_term_given_relevant = (tf + 1) / (sum(term_freq[doc_id].values()) + len(term_doc_freq))
            p_term_given_not_relevant = (df + 1) / (doc_count - df + len(term_doc_freq))
            score *= (p_term_given_relevant / p_term_given_not_relevant)
        scores[doc_id] = score
    return scores

# Flask app setup
app = Flask(__name__)

# Main route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        docs = load_documents(os.path.join(BASE_DIR, 'dataset'))
        term_freq, term_doc_freq, doc_count = compute_statistics(docs)
        query_terms = preprocess(query)
        scores = compute_relevance_prob(query_terms, term_freq, term_doc_freq, doc_count)
        ranked_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return render_template('results.html', query=query, results=ranked_docs[:3])
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

