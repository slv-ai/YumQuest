import os
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from tqdm.auto import tqdm
from dotenv import load_dotenv

load_dotenv()
from postgres import init_db
ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")
MODEL_NAME = os.getenv("MODEL_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")
DATA_PATH = os.getenv("DATA_PATH")


def load_data(data=DATA_PATH):
    df=pd.read_json(data)
    receipes=df.to_dict(orient='records')
    clean_recipes = []
    for recipe in receipes:
        clean_recipe = {key: value for key, value in recipe.items() if key not in ['output', 'date']}
        clean_recipes.append(clean_recipe)
    
    return clean_recipes

def load_model():
    print(f"loading model:{MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

def set_elasticsearch():
            print("setting elasticsearch")
            es_client=Elasticsearch('http://localhost:9200')

            index_settings={
                    "settings":{
                                "number_of_shards":1,
                                "number_of_replicas":0
                            },
                    "mappings":{
                            "properties":{
                                    "title":{"type":"text"},
                                    "tags":{"type":"text"},
                                    "introduction":{"type":"text"},
                                    "ingredients":{"type":"text"},
                                    "direction":{"type":"text"},
                                     "combined_vector":{
                                            "type":"dense_vector",
                                            "dims":384,
                                            "index":True,
                                            "similarity":"cosine"
                                        },
                             },
                    }
            }
            index_name="food_recipes"
            es_client.indices.delete(index=index_name,ignore_unavailable=True)
            es_client.indices.create(index=index_name,body=index_settings)  
            print(f"elastic search created")    
            return es_client

def index_docs(es_client,documents,model):
    print("indexing docs..")
    for recipe in tqdm(documents):
            title = recipe['title']
            ingredients = recipe['ingredients']
            direction = recipe['direction']
            recipe['combined_vector']=model.encode(title + ' '+ ingredients + ' '+ direction )
            try:
                es_client.index(index=INDEX_NAME,document=recipe)  
            except Exception as e:
                print(f"Error indexing document {recipe['title']}: {e}") 
    print(f"indexed {len(documents)} documents")   

def main():
    print(f"starting the indexing..")    
    documents=load_data()
    model=load_model()
    es_client=set_elasticsearch()
    index_docs(es_client,documents,model) 

    print(f"initializing database")
    init_db()
    print("data indexing completed")

if __name__ == "__main__":
    main()

                    
                        
    