# core/encryption.py

from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)


class TokenEncryption:
    
    _key_cache = None
    
    @classmethod
    def _get_key(cls) -> bytes:
        if cls._key_cache is not None:
            return cls._key_cache
        
        try:
            secret = settings.SECRET_KEY.encode('utf-8')
            key_bytes = hashlib.sha256(secret).digest()
            
            cls._key_cache = base64.urlsafe_b64encode(key_bytes)
            
            return cls._key_cache
            
        except Exception as e:
            logger.error(f"Failed to generate encryption key: {str(e)}")
            raise ValueError("Encryption key generation failed")
    
    @classmethod
    def encrypt(cls, token: str) -> str:
        if not token:
            raise ValueError("Token cannot be empty")
        
        try:
            cipher = Fernet(cls._get_key())
            
            token_bytes = token.encode('utf-8')
            encrypted_bytes = cipher.encrypt(token_bytes)
            
            encrypted_str = encrypted_bytes.decode('utf-8')
            
            logger.debug(f"Token encrypted successfully (length: {len(encrypted_str)})")
            
            return encrypted_str
            
        except Exception as e:
            logger.error(f"Token encryption failed: {str(e)}")
            raise ValueError(f"Encryption failed: {str(e)}")
    
    @classmethod
    def decrypt(cls, encrypted_token: str) -> str:
        if not encrypted_token:
            raise ValueError("Encrypted token cannot be empty")
        
        try:
            cipher = Fernet(cls._get_key())
            
            encrypted_bytes = encrypted_token.encode('utf-8')
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            logger.debug("Token decrypted successfully")
            
            return decrypted_str
            
        except Exception as e:
            logger.warning(f"Token decryption failed: {str(e)}")
            raise ValueError(f"Decryption failed - invalid or tampered token")
    
    @classmethod
    def is_encrypted(cls, token: str) -> bool:
        if not token or len(token) < 10:
            return False
        
        return not token.startswith('eyJ')
    
    @classmethod
    def rotate_key(cls):
        cls._key_cache = None
        logger.info("Encryption key cache cleared")

def encrypt_token(token: str) -> str:
    return TokenEncryption.encrypt(token)


def decrypt_token(encrypted_token: str) -> str:
    return TokenEncryption.decrypt(encrypted_token)