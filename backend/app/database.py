import os
from pinecone import Pinecone, ServerlessSpec
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY=")
)

pc = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))
INDEX_NAME = os.getenv("PINECONE_INDEX", "trademind")