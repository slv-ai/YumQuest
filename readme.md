### YumQUEST

## overview
YumQUEST is a recipe discovery application powered by a robust dataset of culinary delights. With the integration of Question-Answering (QA)
chatbot built using Retrieval-Augmented Generation (RAG),YumQUEST aims to enhance your cooking experience by providing personalized suggestions and answers to your culinary questions

## Features

- **Recipe Search**: Users can search for recipes based on ingredients, cuisine, and cooking methods.
- **Q&A Chatbot**: An intelligent chatbot that answers cooking-related queries using RAG to retrieve relevant information from the dataset.
- **User-Friendly Interface**: An easy-to-navigate interface for seamless interaction.

## Dataset

The dataset includes a diverse range of recipes, featuring:

- Ingredients
- Cooking instructions
- Preparation times
- Serving sizes
The dataset is structured in a format suitable for efficient retrieval and interaction with the chatbot.

### Dataset Structure

- `recipes/`
  - `recipe_id`: Unique identifier for each recipe
  - `title`: Name of the dish
  - `ingredients`: List of ingredients
  - `directions`: Step-by-step cooking instructions
 
## Technologies 
  -language : python 3.12
  -LLM : OpenAI(gpt-4o-mini)
  -text search & hybrid search: elastic search
  -interface : streamlit
  -monitoring:grafana
  -containerization: docker-compose
  -Monitoring : grafana


  ## Running the Application

1.Install the required dependencies
  pip install psycopg2-binary python-dotenv
  pip install pgcli

2.first run the docker-compose 
    docker-compose up

3. Run index.py file
     export POSTGRES_HOST="localhost"
     python index.py
  ## Code
The code for the application is in the app folder:

app.py - the streamlit application
rag.py - rag building and evaluation
index.py - loading the data into the knowledge base
postges.py - initalizing database
generate_synthetic_data.py-for grafana monitoring

## Experiments
  It is in notebooks folder
  rag.ipynb - for rag building, retrieval evaluation, rag evaluation
  evaluation_data_generation.ipynb - generate data for evaluation

## RAG Flow Evaluation
 i used LLM as a judge to evaluate rag flow
 i took a sample with 200 records, 
 
 results tested with gpt-4o-mini:
 
 RELEVANT           0.844
 PARTLY_RELEVANT    0.140
 NON_RELEVANT       0.016
 

results for gpt-4o:

RELEVANT           0.748
PARTLY_RELEVANT    0.228
NON_RELEVANT       0.024
i performed hybrid search using gpt-4o-mini.


