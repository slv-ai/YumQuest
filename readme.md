### YumQUEST

## overview
YumQUEST is a recipe discovery application powered by a robust dataset of culinary delights. With the integration of Question-Answering (QA)
chatbot built using Retrieval-Augmented Generation (RAG),YumQUEST aims to enhance your cooking experience by providing personalized suggestions and answers to your culinary questions
![Alt text](https://github.com/slv-ai/YumQuest/blob/main/img1.png)


## 🔧 Tech Stack
- 🧠 Open-source LLM APIs
- 🔍 Elasticsearch (text + vector search)
- 🐳 Docker Compose
- 📊 Grafana for monitoring
- 🖥️ Streamlit UI
- language : python 3.12

## 🚀Features

- Hybrid search: Lexical + semantic search with Elasticsearch
- Real-time Q&A chatbot for cooking recipes
- Token usage and latency monitoring with Grafana
- Fully containerized for easy deployment

## Dataset

The dataset includes a diverse range of recipes, featuring:

- Ingredients
- Cooking instructions
- Preparation times
- Serving sizes
The dataset is structured in a format suitable for efficient retrieval and interaction with the chatbot.

## Dataset Structure

- `recipes/`
  - `recipe_id`: Unique identifier for each recipe
  - `title`: Name of the dish
  - `ingredients`: List of ingredients
  - `directions`: Step-by-step cooking instructions
 
## 📦 How to Run

1.Place your OPENAI API KEY IN .env file and Install the required dependencies
```bash
 - pip install psycopg2-binary python-dotenv
 - pip install pgcli
````
2.To initialize and run PostgreSQL,Elasticsearch,Streamlit,grafana
````bash
   - docker-compose build
   - docker-compose up
`````
3.To run PostgreSQL locally,
````bash
   -  export POSTGRES_HOST="localhost"
````

4.To ingest the script
````bash
   -  python index.py
`````
     
## Code
  The code for the application is in the app folder:

- app.py - the streamlit application
- rag.py - rag building and evaluation
- index.py - loading the data into the knowledge base
- postges.py - initalizing database
- generate_synthetic_data.py-for grafana monitoring

## Experiments
  It is in notebooks folder
  - rag_evaluation.ipynb ->  rag evaluation
  - retrieval_evaluation.ipynb -> retrieval evaluation
  - evaluation_data_generation.ipynb -> generate data for evaluation

## Retrieval Evaluation
  - Hit Rate: 96 %
  - MRR: 85 %

## RAG Flow Evaluation
 - used LLM as a judge to evaluate rag flow
 - took a sample with 200 records, 
 
## results - gpt-4o-mini:
 
 -RELEVANT           0.844
 
 -PARTLY_RELEVANT    0.140
 
 -NON_RELEVANT       0.016 

## results - gpt-4o:

-RELEVANT           0.748

-PARTLY_RELEVANT    0.228

-NON_RELEVANT       0.024

## 📊 Monitoring- grafana to monitor the application
![Alt text](https://github.com/slv-ai/YumQuest/blob/main/img2.png) 
![Alt text](https://github.com/slv-ai/YumQuest/blob/main/img4.png)
![Alt text](https://github.com/slv-ai/YumQuest/blob/main/img3.png)
![Alt text](https://github.com/slv-ai/YumQuest/blob/main/img5.png)
![Alt text](https://github.com/slv-ai/YumQuest/blob/main/img7.png)









