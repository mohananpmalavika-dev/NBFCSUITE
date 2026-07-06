"""
DigiLocker Integration Service
Fetch government-verified documents

Supports:
- OAuth 2.0 authentication
- Document listing
- Document download
- Auto-verified status (government-issued)
"""

import requests
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import logging

from backend.shared.database.integration_models import DigiLockerDocument

logger = logging.getLogger(__name__)


class DigiLockerService:
    """DigiLocker Integration Service"""
    
    def __init__(self, db: Session, tenant_id: int, config: Dict[str, Any]):
        self.db = db
        self.tenant_id = tenant_id
        self.config = config
        self.api_url = config.get('digilocker_api_url', 'https://api.digitallocker.gov.in')
        self.client_id = config.get('digilocker_client_id')
        self.client_secret = config.get('digilocker_client_secret')
        self.redirect_uri = config.get('digilocker_redirect_uri')
    
    def get_authorization_url(self, customer_id: int) -> str:
        """Get OAuth authorization URL"""
        state = hashlib.sha256(f"{customer_id}{datetime.utcnow()}".encode()).hexdigest()
        
        return (
            f"{self.api_url}/oauth2/1/authorize?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"state={state}"
        )
    
    def fetch_documents(
        self,
        customer_id: int,
        authorization_code: str
    ) -> Dict[str, Any]:
        """Fetch documents after OAuth authorization"""
        try:
            # Get access token
            access_token = self._exchange_code_for_token(authorization_code)
            
            # Fetch document list
            documents = self._fetch_document_list(access_token)
            
            # Download and save each document
            saved_docs = []
            for doc in documents:
                saved_doc = self._download_and_save(customer_id, doc, access_token)
                saved_docs.append(saved_doc)
            
            return {
                'success': True,
                'documents_count': len(saved_docs),
                'documents': saved_docs
            }
            
        except Exception as e:
            logger.error(f"DigiLocker: {str(e)}")
            raise
    
    def _exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        response = requests.post(
            f"{self.api_url}/oauth2/1/token",
            data={
                'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code'
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()['access_token']
    
    def _fetch_document_list(self, access_token: str) -> List[Dict]:
        """Fetch list of available documents"""
        response = requests.get(
            f"{self.api_url}/api/1/documents",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('documents', [])
    
    def _download_and_save(
        self,
        customer_id: int,
        doc: Dict[str, Any],
        access_token: str
    ) -> Dict[str, Any]:
        """Download and save document"""
        # Download document
        doc_response = requests.get(
            f"{self.api_url}/api/1/document/{doc['uri']}",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        # Save to storage (S3/MinIO)
        # document_url = save_to_storage(doc_response.content)
        document_url = f"storage://digilocker/{doc['uri']}"
        
        # Save to database
        digilocker_doc = DigiLockerDocument(
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            digilocker_id=doc['uri'],
            document_type=doc['type'],
            document_name=doc['name'],
            document_url=document_url,
            issuer_name=doc.get('issuer'),
            is_verified=True,
            verified_by_govt=True,
            fetched_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        self.db.add(digilocker_doc)
        self.db.commit()
        
        return {
            'id': digilocker_doc.id,
            'type': doc['type'],
            'name': doc['name'],
            'verified': True
        }
