import os
import logging
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse, parse_qs
from azure.storage.blob import BlobServiceClient, ContentSettings

logger = logging.getLogger(__name__)


class AzureUploader:
    def __init__(self, sas_url: Optional[str] = None, container_name: str = "campaign-assets"):
        """
        Initialize Azure Blob Storage uploader with SAS URL.
        
        Args:
            sas_url: Azure Blob Storage SAS URL (e.g., https://account.blob.core.windows.net/container?sp=racwdli...)
            container_name: Default container name (overridden if SAS URL contains container in path)
        """
        self.sas_url = sas_url or os.getenv("AZURE_STORAGE_SAS_URL")
        self.container_name = container_name
        self.enabled = False
        self.blob_service_client: Optional[BlobServiceClient] = None
        
        if self.sas_url:
            try:
                self._init_from_sas_url(self.sas_url)
                self._ensure_container_exists()
                self.enabled = True
                logger.info(f"Azure Blob Storage initialized - container: {self.container_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure Blob Storage: {e}")
                self.enabled = False
        else:
            logger.info("Azure Blob Storage not configured (AZURE_STORAGE_SAS_URL not set)")
    
    def _init_from_sas_url(self, sas_url: str):
        """Initialize from SAS URL with scoped, time-limited permissions"""
        # Parse the SAS URL: https://account.blob.core.windows.net/container?sas_token
        parsed = urlparse(sas_url)
        
        # Extract container name from path (e.g., /campaigncreators -> campaigncreators)
        container_from_url = parsed.path.lstrip('/')
        if container_from_url:
            self.container_name = container_from_url
        
        # Build account URL: https://account.blob.core.windows.net
        account_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # SAS token is the query string (e.g., ?sp=racwdli&st=...)
        sas_token = parsed.query
        
        # Create BlobServiceClient with account URL + SAS token
        self.blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=sas_token
        )
        
        logger.info(f"Initialized with SAS URL - Account: {parsed.netloc}, Container: {self.container_name}")
    
    def _ensure_container_exists(self):
        if not self.blob_service_client:
            return
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created Azure container: {self.container_name}")
        except Exception as e:
            logger.debug(f"Container check skipped (limited SAS permissions): {e}")
    
    def upload_file(self, local_path: Path, blob_name: Optional[str] = None) -> Optional[str]:
        if not self.enabled or not self.blob_service_client:
            logger.debug(f"Azure upload skipped (not enabled): {local_path.name}")
            return None
        
        if not local_path.exists():
            logger.error(f"File not found for upload: {local_path}")
            return None
        
        try:
            if blob_name is None:
                blob_name = str(local_path.relative_to(local_path.parent.parent))
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            content_type = "image/png" if local_path.suffix == ".png" else "application/octet-stream"
            content_settings = ContentSettings(content_type=content_type)
            
            with open(local_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=content_settings
                )
            
            blob_url = blob_client.url
            logger.info(f"Uploaded to Azure: {blob_name} -> {blob_url}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Error uploading file to Azure: {e}")
            return None
    
    def upload_directory(self, directory: Path, prefix: str = "") -> List[str]:
        if not self.enabled:
            logger.debug(f"Azure upload skipped (not enabled): {directory}")
            return []
        
        uploaded_urls = []
        
        for file_path in directory.rglob("*.png"):
            relative_path = file_path.relative_to(directory)
            blob_name = f"{prefix}/{relative_path}" if prefix else str(relative_path)
            
            url = self.upload_file(file_path, blob_name)
            if url:
                uploaded_urls.append(url)
        
        logger.info(f"Uploaded {len(uploaded_urls)} files from {directory} to Azure")
        return uploaded_urls
    
    def delete_blob(self, blob_name: str) -> bool:
        if not self.enabled or not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Deleted from Azure: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting blob from Azure: {e}")
            return False
    
    def list_blobs(self, prefix: str = "", only_images: bool = True) -> List[dict]:
        """List blobs in the container, optionally filtering by prefix and image types"""
        if not self.enabled or not self.blob_service_client:
            logger.debug("Azure listing skipped (not enabled)")
            return []
        
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = []
            image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
            
            for blob in container_client.list_blobs(name_starts_with=prefix):
                # Filter for images only if requested
                if only_images:
                    ext = Path(blob.name).suffix.lower()
                    if ext not in image_extensions:
                        continue
                
                # Get blob URL for preview (safe to display)
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                
                blobs.append({
                    'name': blob.name,
                    'url': blob_client.url,
                    'size': blob.size,
                    'last_modified': blob.last_modified.isoformat() if blob.last_modified else None
                })
            
            logger.info(f"Listed {len(blobs)} blobs from Azure container: {self.container_name}")
            return blobs
            
        except Exception as e:
            logger.error(f"Error listing blobs from Azure: {e}")
            return []
    
    def download_blob(self, blob_name: str, local_path: Path) -> bool:
        """Download a blob from Azure to local filesystem (secure - validates blob exists)"""
        if not self.enabled or not self.blob_service_client:
            logger.debug("Azure download skipped (not enabled)")
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Verify blob exists before downloading
            if not blob_client.exists():
                logger.error(f"Blob does not exist: {blob_name}")
                return False
            
            # Download blob to local file
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                blob_data = blob_client.download_blob()
                f.write(blob_data.readall())
            
            logger.info(f"Downloaded blob from Azure: {blob_name} -> {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading blob from Azure: {e}")
            return False
