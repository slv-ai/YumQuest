import os
import pandas as pd
import psycopg
from pathlib import Path
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
PROJECT_DIR = BASE_DIR.parent
print(PROJECT_DIR)

load_dotenv()
DB_URL = os.getenv("DATABASE_URL","postgresql://yumquest:yumquest@localhost:5434/yumquest")

df = pd.read_json("../data/cleandata_recipes.json")
recipes  = df.to_dict(orient = "records")
print(f"{len(recipes)} recipes & columns :{list(recipes[0].keys())}")

model = SentenceTransformer("all-MiniLM-L12-v2")

inserted_recipes = 0


with psycopg.connect(DB_URL) as conn:
    conn.execute((BASE_DIR/"schema.sql").read_text())
    register_vector(conn)

    for i,recipe in enumerate(recipes, start = 1):
        try:
            title = recipe.get("title","")
            tags = recipe.get("tags","")
            ingredients = recipe.get("ingredients","")
            direction = recipe.get("direction","")

            text = "".join(part for part in [title,ingredients,direction]
                        if part.strip())
            embedding = model.encode(text)

            conn.execute(
                """
                INSERT INTO recipes
                    (title, tags, ingredients, direction, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    title,
                    tags,
                    ingredients,
                    direction,
                    embedding,
                ),
            )

            inserted_recipes += 1
        except Exception as error:
            print(f"error processing recipe{i}:{error}")
            raise
    print(f"recipes inserted {inserted_recipes}")

### RUN THIS COMMAND :psql "postgresql://yumquest:yumquest@localhost:5434/yumquest"
            



