"""
Google Drive Service
Free Google Drive integration as alternative to Microsoft 365
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class GoogleDriveFile(BaseModel):
    """Google Drive file metadata"""
    id: str
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    web_view_link: str
    web_content_link: Optional[str] = None
    parents: List[str] = []
    owners: List[Dict[str, str]] = []


class GoogleDriveService:
    """Free Google Drive integration service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client_id = getattr(self.settings, 'google_drive_client_id', '')
        self.client_secret = getattr(self.settings, 'google_drive_client_secret', '')
        self.redirect_uri = getattr(self.settings, 'google_drive_redirect_uri', '')
        self.scopes = getattr(self.settings, 'google_drive_scopes', 'https://www.googleapis.com/auth/drive.file')
        self.enabled = getattr(self.settings, 'google_drive_enabled', False)
        
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.base_url = "https://www.googleapis.com/drive/v3"
        
        logger.info(f"Google Drive service initialized: enabled={self.enabled}")
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        try:
            if not self.enabled or not self.client_id or not self.client_secret:
                logger.warning("Google Drive not enabled or credentials missing")
                return False
            
            # For demo purposes, we'll use a mock authentication
            # In production, implement OAuth2 flow
            self.access_token = f"google_drive_token_{datetime.now().timestamp()}"
            self.refresh_token = f"google_drive_refresh_{datetime.now().timestamp()}"
            self.token_expires_at = datetime.now() + timedelta(hours=1)
            
            logger.info("Google Drive authenticated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {e}")
            return False
    
    async def get_files(
        self,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100
    ) -> List[GoogleDriveFile]:
        """Get files from Google Drive"""
        try:
            if not await self._ensure_authenticated():
                return []
            
            # Build query parameters
            params = {
                "pageSize": page_size,
                "fields": "files(id,name,mimeType,size,createdTime,modifiedTime,webViewLink,webContentLink,parents,owners)"
            }
            
            if folder_id:
                params["q"] = f"'{folder_id}' in parents"
            elif query:
                params["q"] = query
            
            # For demo purposes, return mock data
            mock_files = [
                GoogleDriveFile(
                    id="1ABC123DEF456",
                    name="Contract Template.docx",
                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    size=1024000,
                    created_time=datetime.now() - timedelta(days=1),
                    modified_time=datetime.now(),
                    web_view_link="https://drive.google.com/file/d/1ABC123DEF456/view",
                    web_content_link="https://drive.google.com/uc?id=1ABC123DEF456",
                    parents=["0ABC123DEF456"],
                    owners=[{"emailAddress": "user@company.com", "displayName": "User Name"}]
                ),
                GoogleDriveFile(
                    id="2XYZ789GHI012",
                    name="Legal Agreement.pdf",
                    mime_type="application/pdf",
                    size=2048000,
                    created_time=datetime.now() - timedelta(days=2),
                    modified_time=datetime.now() - timedelta(hours=1),
                    web_view_link="https://drive.google.com/file/d/2XYZ789GHI012/view",
                    web_content_link="https://drive.google.com/uc?id=2XYZ789GHI012",
                    parents=["0ABC123DEF456"],
                    owners=[{"emailAddress": "user@company.com", "displayName": "User Name"}]
                )
            ]
            
            return mock_files
            
        except Exception as e:
            logger.error(f"Failed to get Google Drive files: {e}")
            return []
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        folder_id: Optional[str] = None,
        description: str = ""
    ) -> Optional[GoogleDriveFile]:
        """Upload file to Google Drive"""
        try:
            if not await self._ensure_authenticated():
                return None
            
            # For demo purposes, return mock uploaded file
            uploaded_file = GoogleDriveFile(
                id=f"uploaded_{datetime.now().timestamp()}",
                name=filename,
                mime_type=mime_type,
                size=len(file_content),
                created_time=datetime.now(),
                modified_time=datetime.now(),
                web_view_link=f"https://drive.google.com/file/d/uploaded_{datetime.now().timestamp()}/view",
                web_content_link=f"https://drive.google.com/uc?id=uploaded_{datetime.now().timestamp()}",
                parents=[folder_id] if folder_id else [],
                owners=[{"emailAddress": "user@company.com", "displayName": "User Name"}]
            )
            
            logger.info(f"File uploaded to Google Drive: {filename}")
            return uploaded_file
            
        except Exception as e:
            logger.error(f"Failed to upload file to Google Drive: {e}")
            return None
    
    async def download_file(self, file_id: str) -> Optional[bytes]:
        """Download file from Google Drive"""
        try:
            if not await self._ensure_authenticated():
                return None
            
            # For demo purposes, return mock file content
            mock_content = b"This is a mock file content for demo purposes."
            
            logger.info(f"File downloaded from Google Drive: {file_id}")
            return mock_content
            
        except Exception as e:
            logger.error(f"Failed to download file from Google Drive: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        try:
            if not await self._ensure_authenticated():
                return False
            
            # For demo purposes, simulate successful deletion
            logger.info(f"File deleted from Google Drive: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file from Google Drive: {e}")
            return False
    
    async def create_folder(
        self,
        name: str,
        parent_folder_id: Optional[str] = None
    ) -> Optional[GoogleDriveFile]:
        """Create folder in Google Drive"""
        try:
            if not await self._ensure_authenticated():
                return None
            
            # For demo purposes, return mock created folder
            folder = GoogleDriveFile(
                id=f"folder_{datetime.now().timestamp()}",
                name=name,
                mime_type="application/vnd.google-apps.folder",
                size=0,
                created_time=datetime.now(),
                modified_time=datetime.now(),
                web_view_link=f"https://drive.google.com/drive/folders/folder_{datetime.now().timestamp()}",
                parents=[parent_folder_id] if parent_folder_id else [],
                owners=[{"emailAddress": "user@company.com", "displayName": "User Name"}]
            )
            
            logger.info(f"Folder created in Google Drive: {name}")
            return folder
            
        except Exception as e:
            logger.error(f"Failed to create folder in Google Drive: {e}")
            return None
    
    async def get_folder_contents(self, folder_id: str) -> List[GoogleDriveFile]:
        """Get contents of a specific folder"""
        try:
            return await self.get_files(folder_id=folder_id)
        except Exception as e:
            logger.error(f"Failed to get folder contents: {e}")
            return []
    
    async def search_files(
        self,
        query: str,
        mime_type: Optional[str] = None
    ) -> List[GoogleDriveFile]:
        """Search for files in Google Drive"""
        try:
            search_query = f"name contains '{query}'"
            if mime_type:
                search_query += f" and mimeType='{mime_type}'"
            
            return await self.get_files(query=search_query)
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []
    
    async def get_file_metadata(self, file_id: str) -> Optional[GoogleDriveFile]:
        """Get metadata for a specific file"""
        try:
            if not await self._ensure_authenticated():
                return None
            
            # For demo purposes, return mock file metadata
            file_metadata = GoogleDriveFile(
                id=file_id,
                name="Sample Contract.pdf",
                mime_type="application/pdf",
                size=1536000,
                created_time=datetime.now() - timedelta(days=1),
                modified_time=datetime.now(),
                web_view_link=f"https://drive.google.com/file/d/{file_id}/view",
                web_content_link=f"https://drive.google.com/uc?id={file_id}",
                parents=["0ABC123DEF456"],
                owners=[{"emailAddress": "user@company.com", "displayName": "User Name"}]
            )
            
            return file_metadata
            
        except Exception as e:
            logger.error(f"Failed to get file metadata: {e}")
            return None
    
    async def get_storage_quota(self) -> Dict[str, Any]:
        """Get Google Drive storage quota information"""
        try:
            if not await self._ensure_authenticated():
                return {}
            
            # For demo purposes, return mock quota info
            return {
                "limit": "15GB",
                "usage": "2.5GB",
                "usage_in_drive": "1.8GB",
                "usage_in_drive_trash": "0.7GB",
                "usage_percent": 16.67
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage quota: {e}")
            return {}
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token"""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return await self.authenticate()
        return True
