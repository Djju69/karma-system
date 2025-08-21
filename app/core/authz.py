"""
Authorization service for Karma System.
"""
from typing import Dict, Optional
from app.db.models import UserRole

class AuthzService:
    """Authorization service for role-based access control."""
    
    def is_admin(self, user: Dict) -> bool:
        """Check if user is admin."""
        return user.get('role') == UserRole.ADMIN
    
    def is_partner(self, user: Dict) -> bool:
        """Check if user is partner."""
        return user.get('role') == UserRole.PARTNER
    
    def is_owner(self, user: Dict, listing: Dict) -> bool:
        """Check if user owns the listing."""
        return user.get('id') == listing.get('user_id')
    
    def can_create_qr(self, user: Dict, listing: Dict) -> bool:
        """Check if user can create QR for listing."""
        # Must be owner or admin
        if not (self.is_owner(user, listing) or self.is_admin(user)):
            return False
        
        # Listing must be approved and not hidden
        if listing.get('moderation_status') != 'approved':
            return False
        
        if listing.get('is_hidden'):
            return False
        
        return True
    
    def can_scan_qr(self, user: Dict) -> bool:
        """Check if user can scan QR codes."""
        return self.is_partner(user) or self.is_admin(user)
    
    def can_moderate(self, user: Dict) -> bool:
        """Check if user can moderate listings."""
        return self.is_admin(user)
    
    def can_manage_cities(self, user: Dict) -> bool:
        """Check if user can manage cities."""
        return self.is_admin(user)

# Global service instance
authz_service = AuthzService()
