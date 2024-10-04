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

model_name='gpt-4o-mini'
index_name="food_recipes"

def elastic_search_text(query, index_name="food_recipes"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "introduction", "direction"],
                        "type": "best_fields",
                    }
                },
                
            }
        },
    }

    response = es_client.search(index=index_name, body=search_query)
    return [hit["_source"] for hit in response["hits"]["hits"]]



def elastic_search_knn_query(field,vector):
            knn={
                "field":field,
                "query_vector":vector,
                "k":5,
                "num_candidates": 360,
            }
            search_query={
                "knn":knn,
                "_source":["title","tags","introduction","ingredients","direction"]
            }
            es_results=es_client.search(index=index_name,body=search_query)
            results=[]
            for hit in es_results['hits']['hits']:
                    results.append(hit['_source'])
            return results
            

def build_prompt(query,search_results):
        prompt_template = """
            you are a chefs assistant . Answer the QUESTION based on CONTEXT from the  database.
            use only the facts from the CONTEXT when answering the QUESTION.
        QUESTION:{question}
        CONTEXT:{context}
        """.strip()
        context=""
        for doc in search_results:
                    context = context + f"title : {doc['title']} \n tags : {doc['tags']} \n introduction : {doc['introduction']} \n ingredients :{doc['ingredients']} \n direction : {doc['direction']}\n\n"
        prompt=prompt_template.format(question=query,context=context).strip()
        return prompt

def llm(prompt,model=model_name):
        start_time=time.time()
        response=client.chat.completions.create(model=model_name,
                                            messages=[{"role":"user","content":prompt}]
                                            )
        answer= response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
        end_time=time.time()
        response_time=end_time-start_time
        return answer,tokens,response_time


def evaluate_relevance(question, answer):
    prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
    Your task is to analyze the relevance of the generated answer to the given question.
    Based on the relevance of the generated answer, you will classify it
    as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()

    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, 'openai/gpt-4o-mini')
    
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens

def calculate_openai_cost(tokens):
    openai_cost = 0

    openai_cost = (tokens['prompt_tokens'] * 0.03 + tokens['completion_tokens'] * 0.06) / 1000

    return openai_cost

def get_answer(query, search_type):
    if search_type == 'Vector':
        vector_query = model.encode(query)
        search_results = elastic_search_knn_query('combined_vector', vector_query)
    else:
        search_results = elastic_search_text(query)

    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model=model)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

    openai_cost = calculate_openai_cost(tokens)
 
    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': openai_cost
    }