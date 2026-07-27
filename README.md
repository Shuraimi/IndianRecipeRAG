# Indian Recipe RAG

## Problem Statement
Suppose we have a recipe book and we want to search for a recipe not with it's name but by describing the recipe or the ingredients we have currently.
This is where RAG comes in and solves the problem.
My project, Indian Recipe RAG gives the user the most similar recipe to his query from the Knowledge Base(ChromaDB in this case)

## Data
The data I have used for this project is the recipes which have been scrapped by Kanishk and uploaded on GitHub.
The link to the dataset : https://github.com/kanishk307/IndianFoodDatasetGeneration
I have only selected Indian Recipes from the dataset. 


## Project structure/architecture

```mermaid
flowchart TD

A[User] --> B[Streamlit UI<br/>app.py]

B --> C[RAG Pipeline<br/>ragClass.py]

C --> D[History Aware Retriever]
C --> E[Chroma Vector Database]
C --> F[Groq LLM]

D --> G[Pydantic Output Parser<br/>pydantic_parser.py]
E --> G
F --> G

G --> H[Structured Recipe Response]

H --> I[SQLite Analytics Database <br/>analytics.db]

I --> J[Monitoring Dashboard]
```

## 🛠️ Tech Stack

* 💻 **Python** – Core programming language
* 🧪 **Jupyter Notebook** – Experimentation and development before deployment
* ⚙️ **LangChain** – RAG pipeline, prompt templates, retrievers, chains, and output parsing
* 🗄️ **ChromaDB** – Vector database for semantic recipe retrieval
* 🎨 **Streamlit** – Web application and analytics dashboard
* 🗄️ **SQLite** – Logging requests, token usage, latency, model usage, and user feedback
* 📊 **Plotly** – Interactive dashboard visualizations

**Models Used**

* **Embedding Model (Hugging Face)**

  * `BAAI/bge-small-en-v1.5`

* **LLMs (via ChatGroq)**

  * `llama-3.1-8b-instant`
  * `llama-3.3-70b-versatile`
  * `openai/gpt-oss-20b`
  * `openai/gpt-oss-safeguard-20b`


## File structure

```text
Recipe-RAG/
│
├── app.py                      # Main Streamlit application
├── ragClass.py                 # RAG pipeline (retrieval + generation)
├── database.py                 # SQLite database operations and logging
├── pydantic_parser.py          # Pydantic output schema
├── Analytics.py                # Monitoring dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env                        # API keys (not committed)
│
├── recipe_db/                  # Chroma vector database
│   ├── chroma.sqlite3
│   └── ...
│
├── analytics.db                # SQLite monitoring database
│
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
├── dataset/
│   ├── dataset.json
│   └── indian_recipes_rag_dataset.csv
│
├── images/                     # README screenshots
│   ├── UI.png
|   ├── input output display.png
|   ├── output and model selection.png
|   ├── dashboard.png
|   ├── dashboard2.png
│   └── dashboard3.png
│
└── notebooks/                  # Development notebooks 
    └── experimentation.ipynb
```
## Retrieval evalution

I tried vector search and used and compared retrievers with search type similarity, similarity score and mmr and the selected MMR

I also tried BM25 which is a keyword search and also tried Hybrid search which included vector search and BM25.

But both gave similar results, so selected vector search with MMR as retriever for my project.

## LLM evaluation

I tried various prompts in the notebook while developing and then selected the last one which gave good result.


## Screenshots:-
### UI
<img src='UI images\UI.png'>

### Input Output
<img src='UI images\input output display.png'>

### Dashboard
<img src='UI images\dashboard.png'>
<img src='UI images\dashboard2.png'>
<img src='UI images\dashboard3.png'>

### Output and model selection display
<img src='UI images\output and model selection.png'>


## How to run the project/app?

### 1. Online ( through Streamlit)

I have deployed the app onto streamlit. So check out the app there :- https://indianreciperag.streamlit.app/

### 2. Locally

You can use the app locally.
For this you just need to follow the steps below:-
1. Clone the repo
```
git clone https://github.com/Shuraimi/IndianRecipeRAG.git
```
2. move to the directory of the cloned repo
```
cd your_cloned_directory_path
```
3. pip install libraries required for the project locally from the requirements.txt file
```
pip install -r requirements.txt
```
4. create a .env file and add your groq API key 
```
GROQ_API_KEY='YOUR_API_KEY'
```
5. then in the cmd, activate the environment and run 
```
streamlit run app.py
```

Check out the app on your browser

## App preview
<video  controls>
<source src='videos\indian recipe RAG walkthrough.mp4'>
</video>

## 📝 Implementation Overview

The development process began in a Jupyter Notebook, where I experimented with different components of the Retrieval-Augmented Generation (RAG) pipeline, including data preprocessing, embedding generation, vector storage, retrieval strategies, prompt engineering, and structured output parsing. You can explore the complete experimentation process in the notebook linked above.

Notebook :- notebooks\experimentation.ipynb

After validating the pipeline, I modularized the project into separate Python scripts:

* **`ragClass.py`** – Implements the complete RAG pipeline, including the history-aware retriever, vector database integration, prompt templates, and LLM interaction.
* **`app.py`** – Provides the Streamlit-based chat interface for interacting with the recipe recommendation system.
* **`pydantic_parser.py`** – Defines the structured response schema, ensuring that every generated recipe follows a consistent format.

To monitor the application's performance, I developed a dedicated **Analytics** page in Streamlit. This dashboard visualizes key metrics such as request latency, model usage, input and output token consumption, user feedback, and recent requests.

A separate **`database.py`** module manages the SQLite database used for monitoring. It creates the required tables, logs every LLM request, and provides helper functions to retrieve aggregated statistics such as average latency, average token usage, feedback distribution, and model usage, which are then displayed in the analytics dashboard.

Finally, I added support for **dynamic model selection**, allowing users to switch between multiple Groq-hosted language models directly from the application. To enable this, the original `build_chain()` method was replaced with an `update_chain()` method, which recreates the `ChatGroq` instance and rebuilds the associated LangChain components whenever a different model is selected, ensuring the RAG pipeline always uses the currently chosen model.


## What I learnt?

1. Building a monitoring dashboard using Streamlit
2. Using SQLiteDB for storing the logs for analytical monitoring
3. Various Streamlit components while buidling the app.

## Further improvements

- replace SQLiteDB with PostgreSQLDB hosted on SupaBase

## How I used AI?

> I used ChatGPT for various pat of my project to guide me and explain the code and I wrote the code instead of copy pasting.
> Claude gave me the dataset to inlcude only indian recipes from the original list of 6000 recipes 