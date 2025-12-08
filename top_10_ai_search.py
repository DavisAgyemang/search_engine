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


def get_top_10_unique_results(query_text, status):
    print(f"\n🔎 Fetching Top 10 Unique Results for: '{query_text}'")

    # 1. Vectorize input
    query_vector = embed.embed_query(query_text)

    # 2. window expansion: request more than 10 (e.g., 40)
    # This accounts for chunks being duplicates of the same document title.
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=40,  # Increase search window to find enough unique matches
        fields="embedding"
    )
    filter_expr = f"status eq '{status}'" if status else None

    # 3. Execute search with an expanded 'top' parameter
    results = client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=filter_expr,
        select=["title", "rm_number", "summary"],
        top=40
    )

    # 4. Deduplication Logic
    top_results = []
    seen_titles = set()

    for res in results:
        title = res['title']

        # Check if we've already added this framework title
        if title not in seen_titles:
            top_results.append(res)
            seen_titles.add(title)

        # Stop exactly once we have 10 unique documents
        if len(top_results) == 10:
            break

    # 5. Process and print result list
    print(f"{'Rank':<5} | {'Title':<40} | {'Score':<10}")
    print("-" * 60)

    for i, res in enumerate(top_results):
        # res['@search.score'] will be based on the best chunk found for that title
        print(f"{i + 1:<5} | {res['title'][:38]:<40} | {res['@search.score']:.4f}")

    return top_results
# --- Usage Example ---
results = get_top_10_unique_results("AWS", status="Live")