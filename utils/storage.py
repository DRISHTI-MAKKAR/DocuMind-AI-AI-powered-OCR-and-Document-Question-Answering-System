import os
from azure.storage.blob import BlobServiceClient


def upload_to_blob(file_bytes: bytes, filename: str) -> str:
    """Upload file to Azure Blob Storage. Returns the blob URL."""
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    container = os.getenv("AZURE_CONTAINER_NAME", "question-papers")

    if not conn_str:
        return ""  # Skip if not configured

    client = BlobServiceClient.from_connection_string(conn_str)
    container_client = client.get_container_client(container)

    # Create container if it doesn't exist
    try:
        container_client.create_container()
    except Exception:
        pass  # Already exists

    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file_bytes, overwrite=True)

    return blob_client.url


def list_blobs() -> list[str]:
    """List all uploaded files in the container."""
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    container = os.getenv("AZURE_CONTAINER_NAME", "question-papers")

    if not conn_str:
        return []

    client = BlobServiceClient.from_connection_string(conn_str)
    container_client = client.get_container_client(container)

    try:
        return [blob.name for blob in container_client.list_blobs()]
    except Exception:
        return []


def download_blob(filename: str) -> bytes:
    """Download a file from Azure Blob Storage."""
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    container = os.getenv("AZURE_CONTAINER_NAME", "question-papers")

    client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = client.get_container_client(container).get_blob_client(filename)
    return blob_client.download_blob().readall()
