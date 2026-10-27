import os
import time
import psycopg
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()
DB_URL = os.getenv("DATABASE_URL","postgresql://yumquest:yumquest@localhost:5434/yumquest")
MODEL = "gpt-4o-mini"
PRICE_IN , PRICE_OUT = 0.15 , 0.60

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY not found")

embedder = SentenceTransformer("all-MiniLM-L12-v2")
client = OpenAI()

def get_conn():
    conn = psycopg.connect(DB_URL)
    register_vector(conn)
    return conn

def search(query, k=5):
    query_vec = embedder.encode(query)
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id, title, tags, ingredients, direction
            FROM recipes
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (query_vec, k),
        ).fetchall()

def build_prompt(query,recipes):
    context =""
    for id, title, tags, ingredients, direction in recipes:
        context += f"RECIPE: {title}\ntags: {tags}\nIngredients: {ingredients}\nDirections: {direction[:1500]}\n\n"
    return (
        "You are a helpful chef assistant. Answer the QUESTION using only the recipes in CONTEXT.\n"
        "If none of them fit, say so. Mention the title of each recipe you use.\n\n"
        f"CONTEXT:\n{context}\n"
        f"QUESTION: {query}"
    )

def ask_llm(prompt):
    start = time.time()
    response = client.chat.completions.create(model=MODEL, messages= [{"role" : "user","content" : prompt }])
    seconds = time.time() - start
    answer = response.choices[0].message.content or ""
    p_tok, c_tok = response.usage.prompt_tokens , response.usage.completion_tokens
    cost = (p_tok * PRICE_IN + c_tok * PRICE_OUT) / 1_000_000
    return answer, p_tok, c_tok, cost, seconds

def save_conversation(query, answer, recipe_ids, p_tok, c_tok, cost, seconds):

    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO conversations (question, answer, model, recipe_ids, prompt_tokens, "
            "response_tokens, cost_usd, response_seconds) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (query, answer, MODEL, recipe_ids, p_tok, c_tok, cost, seconds),
        ).fetchone()[0]

def save_feedback(conversation_id, value):
    with get_conn() as conn:
        conn.execute("UPDATE conversations SET feedback = %s WHERE id = %s", (value, conversation_id))

def recent_conversations(limit = 5):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id, question, model, cost_usd,
                feedback, created_at
            FROM conversations
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()


def answer_query(query):
    recipes = search(query)
    prompt = build_prompt(query, recipes)
    answer , p_tok, c_tok, cost, total_time = ask_llm(prompt)
    conv_id = save_conversation(query, answer, [r[0] for r in recipes], p_tok, c_tok, cost, total_time)
    return {"id": conv_id, "answer": answer, "recipes": recipes, "model": MODEL,
            "prompt_tokens": p_tok, "response_tokens": c_tok, "cost": cost, "seconds": total_time}