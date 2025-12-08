from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from fastapi import  FastAPI
from pydantic import BaseModel

load_dotenv()

embed = AzureOpenAIEmbeddings(
    model= os.getenv("EMBEDDING_MODEL_NAME"),
    api_key= os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint= os.getenv("EMBEDDING_ENDPOINT"),
    api_version= os.getenv("AZURE_OPENAI_API_VERSION")
)

client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name=os.getenv("SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("ADMIN_KEY"))
)


def evaluate_retrieval(user_query, target_title, k=3):
    """
    Checks if the expected title appears in the top results.
    Returns the rank (1-based) if found, else 0.
    """
    # 2. Vectorize user input
    query_vector = embed.embed_query(user_query)

    # 3. Search the vector field
    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=k, fields="embedding")

    results = client.search(
        search_text=None,  # Pure vector search
        vector_queries=[vector_query],
        select=["title", "rm_number"]
    )

    # 4. Check results
    retrieved_titles = [row['title'] for row in results]

    if target_title in retrieved_titles:
        rank = retrieved_titles.index(target_title) + 1
        print(f"✅ Success! Query: '{user_query}' -> Found '{target_title}' at Rank #{rank}")
        return rank
    else:
        print(
            f"❌ Failed. Query: '{user_query}' -> Expected '{target_title}' NOT in top {k}. Top result: {retrieved_titles[0]}")
        return 0


# --- Test Suite ---
# Format: ("User Input Query", "Ground Truth Product Title")
test_cases = [
    ("Adult skills training funding", "Adult Skills and Learning DPS"),
    ("Medical imaging software for health bodies", "Artificial Intelligence (AI)"),
    ("Blue light services AI procurement", "Artificial Intelligence (AI)"),
   ("ai", "Artificial Intelligence (AI)"),
    ("understanding machine learning benefits", "Artificial Intelligence (AI)"),
    ("non-apprenticeship vocational development", "Adult Skills and Learning DPS")
]

top1_count = 0
found_count = 0

for q, target in test_cases:
    rank = evaluate_retrieval(q, target)
    if rank == 1: top1_count += 1
    if rank > 0: found_count += 1

print(f"\n--- Results Summary ---")
print(f"Top-1 Accuracy: {(top1_count / len(test_cases)) * 100:.1f}%")
print(f"Overall Success Rate (in Top 3): {(found_count / len(test_cases)) * 100:.1f}%")