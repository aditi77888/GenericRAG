import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index("pinecone-api")

stats = index.describe_index_stats()

print("Namespaces found:")
print(stats.namespaces)

for namespace in stats.namespaces:

    print(f"Deleting namespace: {namespace}")

    index.delete(
        delete_all=True,
        namespace=namespace
    )

    print(f"Deleted: {namespace}")

print("\nAll Pinecone vectors deleted successfully.")