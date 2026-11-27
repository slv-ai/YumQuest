import os
import logging
import time
import psycopg
from dotenv import load_dotenv
from openai import OpenAI
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

load_dotenv()
log = logging.getLogger("yumquest")

DB_URL = os.getenv("DATABASE_URL","postgresql://yumquest:yumquest@localhost:5434/yumquest")
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER","openai")
TOP_K = int(os.getenv("TOP_K", "5"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))               # seconds to wait for the LLM
MAX_QUESTION_CHARS = 1000

MODELS = {
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "bedrock": os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
}

PRICES = {
    "gpt-4o-mini": (0.15, 0.60),
    "us.amazon.nova-lite-v1:0": (0.06, 0.24),
}


client = OpenAI()

def get_embedder():
    try:
        embedder = SentenceTransformer("all-MiniLM-L12-v2")
    except Exception as e:
            raise RuntimeError("Could not load the embedding model")from e
    
    return embedder

def get_conn():
    conn = psycopg.connect(DB_URL)
    register_vector(conn)
    return conn

def search(query, k=TOP_K):
    query_vec = get_embedder.encode(query)
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

def estimate_cost(model,p_tok,c_tok):
    if model not in PRICES:
        return None
    price_in , price_out = PRICES
    return (p_tok * price_in + c_tok * price_out) / 1_000_000

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        try:
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI API KEY NOT FOUND")
        except Exception as e:
            raise RuntimeError (f"Could not initialize OpenAI client: {e}") from e
        _openai_client = OpenAI(api_key=key, timeout=LLM_TIMEOUT, max_retries=2)
    return _openai_client


def ask_openai(prompt):
    
    client = get_openai_client()
    start = time.time()
    response = client.chat.completions.create(model=MODELS["openai"], messages= [{"role" : "user","content" : prompt }])
    seconds = time.time() - start
    answer = response.choices[0].message.content or ""
    p_tok, c_tok = response.usage.prompt_tokens , response.usage.completion_tokens
    
    return answer, p_tok, c_tok, estimate_cost(MODELS["openai"],p_tok,c_tok), seconds

def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        import boto3
        from botocore.config import Config
        _bedrock_client = boto3.client(
            "bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"),
            config=Config(connect_timeout=10, read_timeout=LLM_TIMEOUT,
                        retries={"max_attempts": 3, "mode": "standard"}))
    return _bedrock_client

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