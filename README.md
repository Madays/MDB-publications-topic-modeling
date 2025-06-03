# 🌍 MDB Publications Topic Modeling

This project performs **unsupervised topic modeling** on public development-related documents retrieved from the **World Bank API**. The aim is to extract meaningful themes and topics from abstracts of publications related to sustainable development, policy, energy, and more.

---

## 📦 Project Structure

```
your_project_name/
├── data/
│   ├── raw/            # Original, unprocessed data
│   ├── interim/        # Data that has been cleaned and preprocessed
│   └── processed/      # Final, ready-to-use datasets for modeling
├── notebooks/          # Jupyter notebooks for exploration, experimentation, and analysis
│   ├── 01_data_understanding.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_selection.ipynb
├── src/                # Source code for your project (Python modules, scripts)
│   ├── data/           # Modules for data loading and preprocessing
│   ├── features/       # Modules for feature engineering
│   ├── models/         # Modules for model training and evaluation
│   ├── visualization/  # Modules for creating visualizations
│   └── utils/          # Utility functions and helper scripts
├── models/             # Saved trained models (e.g., .pkl, .h5 files)
├── reports/            # Generated reports and visualizations
│   ├── figures/
│   └── tables/
├── docs/               # Project documentation
│   └── README.md
├── deployment/         # Deployment-ready structure
│   ├── api/
│   ├── batch/
│   ├── cloud/
│   ├── scripts/
│   └── model/
├── config/             # Configuration files (e.g., paths, hyperparameters)
├── .gitignore
├── requirements.txt
└── environment.yml
```

---

## 🚀 How It Works

1. **Fetch documents** from the World Bank API using a set of predefined taxonomy topics.
2. **Clean and filter** the data using `pandas`: remove empty abstracts, filter by language, drop duplicates.
3. **Stratify** by query to ensure balanced topic representation.
4. **Preprocess** text: lowercase, tokenize, remove stopwords.
5. **Model** topics using LDA or BERTopic.
6. **Evaluate** and visualize discovered topics.

---

## 🛠️ Tech Stack

- `pandas` — data manipulation
- `requests` — fetch data via HTTP
- `gensim`, `scikit-learn` — LDA modeling
- `BERTopic`, `umap-learn`, `hdbscan` — advanced topic modeling
- `matplotlib`, `pyLDAvis` — visualizations

---

## 📊 Example Output

- Topic clusters visualized in 2D space
- Top keywords per topic
- Topic distribution across taxonomy queries

---

## 📁 Key Files

- `download_raw_data.py` — fetches and stores documents
- `stratified_sampling.py` — balances samples by query
- `notebooks/` — step-by-step topic modeling exploration
- `worldbank_documents.csv` — raw corpus

---

## 📌 Getting Started

```bash
# Create and activate environment
conda env create -f environment.yml
conda activate worldbank-topic-modeling

# Install requirements (optional)
pip install -r requirements.txt

# Run main data collection script
python src/data/download_raw_data.py
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT License — see `LICENSE` file for details.

---

## 🌐 References

- [World Bank Document API](https://documents.worldbank.org/en/publication/documents-reports/api)

---

Need help running this project or deploying it? Open an issue or contact the maintainer.
