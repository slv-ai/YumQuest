import os
import json
import time
from openai import OpenAI
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELASTIC_URL=os.getenv("ELASTIC_URL")

es_client=Elasticsearch(ELASTIC_URL)
client = OpenAI(api_key=OPENAI_API_KEY)

