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
language : python 3.12

LLM : OpenAI(gpt-4o-mini)

text search & hybrid search: elastic search

interface : streamlit

monitoring:grafana

containerization: docker-compose


Monitoring : grafana
