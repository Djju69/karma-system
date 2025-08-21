"""
Database models for Karma System.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, Numeric, Index, UniqueConstraint, func, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geography
import uuid

Base = declarative_base()

class UserRole(str, Enum):
    USER = "user"
    PARTNER = "partner"
    ADMIN = "admin"

class PartnerStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class QRStatus(str, Enum):
    ISSUED = "issued"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    REVOKED = "revoked"

class ModerationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Category(str, Enum):
    RESTAURANTS = "restaurants"
    SPA = "spa"
    TRANSPORT = "transport"
    HOTELS = "hotels"
    TOURS = "tours"

class City(Base):
    """Cities where system operates."""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    name_ru = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)
    name_vi = Column(String(100), nullable=False)
    name_ko = Column(String(100), nullable=False)
    lat = Column(Numeric(10, 8))
    lng = Column(Numeric(11, 8))
    coverage_area = Column(Geography('POLYGON'))
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="city")
    listings = relationship("Listing", back_populates="city")
    partner_applications = relationship("PartnerApplication", back_populates="city")
    
    # Indexes
    __table_args__ = (
        Index('idx_cities_active', 'is_active'),
        Index('idx_cities_default', 'is_default'),
    )

class User(Base):
    """Telegram users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(String(20), unique=True, nullable=False)
    role = Column(String(20), default=UserRole.USER)
    lang = Column(String(10), default="ru")
    city_id = Column(Integer, ForeignKey("cities.id"))
    policy_accepted = Column(Boolean, default=False)
    blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    city = relationship("City", back_populates="users")
    partner_profile = relationship("PartnerProfile", back_populates="user", uselist=False)
    partner_auth = relationship("PartnerAuth", back_populates="user", uselist=False)
    listings = relationship("Listing", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_tg_id', 'tg_id'),
        Index('idx_users_role', 'role'),
    )

class PartnerProfile(Base):
    """Partner profiles."""
    __tablename__ = "partner_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(200), nullable=False)
    phone_hash = Column(String(64), nullable=False)  # SHA-256 + salt
    settings = Column(JSONB, default={})
    notify = Column(JSONB, default={
        "qr": True,
        "moderation": True,
        "block": True,
        "system": True
    })
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="partner_profile")
    listings = relationship("Listing", back_populates="partner_profile")

class PartnerAuth(Base):
    """Partner web authentication."""
    __tablename__ = "partner_auth"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="partner_auth")

class Listing(Base):
    """Business listings."""
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    partner_profile_id = Column(Integer, ForeignKey("partner_profiles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Owner for quick checks
    category = Column(String(20), nullable=False)  # restaurants, spa, transport, hotels, tours
    sub_slug = Column(String(50))  # For restaurants: asia, europe, street, vege
    name = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(Text, nullable=False)
    gmaps_url = Column(String(500))
    phone = Column(String(20))
    district = Column(String(100))
    brand_logo_url = Column(String(500))
    moderation_status = Column(String(20), default=ModerationStatus.PENDING)
    priority_level = Column(Integer, default=0)
    priority_until = Column(DateTime)
    is_hidden = Column(Boolean, default=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    city = relationship("City", back_populates="listings")
    partner_profile = relationship("PartnerProfile", back_populates="listings")
    user = relationship("User", back_populates="listings")
    qr_issues = relationship("QRIssue", back_populates="listing")
    
    # Indexes
    __table_args__ = (
        Index('idx_listings_city_category_status', 'city_id', 'category', 'moderation_status'),
        Index('idx_listings_priority', 'priority_level', postgresql_using='btree', postgresql_ops={'priority_level': 'DESC'}),
        Index('idx_listings_user', 'user_id'),
    )

class QRIssue(Base):
    """QR code issues for karma earning."""
    __tablename__ = "qr_issues"
    
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    issued_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default=QRStatus.ISSUED)
    expires_at = Column(DateTime, nullable=False)
    redeemed_at = Column(DateTime)
    redeemed_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    listing = relationship("Listing", back_populates="qr_issues")
    issued_by = relationship("User", foreign_keys=[issued_by_user_id])
    redeemed_by = relationship("User", foreign_keys=[redeemed_by_user_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_qr_issues_jti', 'jti'),
        Index('idx_qr_issues_listing_status', 'listing_id', 'status'),
        Index('idx_qr_issues_expires', 'expires_at'),
    )

class PartnerApplication(Base):
    """Partner applications."""
    __tablename__ = "partner_applications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_name = Column(String(100), nullable=False)
    contact_phone = Column(String(64), nullable=False)  # Hashed
    contact_email = Column(String(100))
    telegram_username = Column(String(100))
    business_name = Column(String(200), nullable=False)
    business_address = Column(Text, nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    category = Column(String(20), nullable=False)
    category_id = Column(Integer)
    description = Column(Text)
    website = Column(String(200))
    instagram = Column(String(100))
    average_check = Column(Integer)
    status = Column(String(20), default=PartnerStatus.PENDING)
    rejection_reason = Column(Text)
    processed_at = Column(DateTime)
    partner_id = Column(Integer, ForeignKey("partner_profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    city = relationship("City", back_populates="partner_applications")
    partner_profile = relationship("PartnerProfile")
    
    # Indexes
    __table_args__ = (
        Index('idx_partner_applications_status', 'status'),
        Index('idx_partner_applications_city', 'city_id'),
    )

class Transaction(Base):
    """Karma transactions history."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    
    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"))
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"))
    
    # Transaction details
    type = Column(String(20), nullable=False)  # TransactionType
    amount = Column(Integer, nullable=False)  # karma amount (can be negative)
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    
    # Metadata
    description = Column(String(500))
    order_amount = Column(Integer)  # original order amount if applicable
    reference_id = Column(String(100))  # external reference
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    partner = relationship("Partner", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_transactions_user_created', 'user_id', 'created_at'),
        Index('idx_transactions_partner_created', 'partner_id', 'created_at'),
        Index('idx_transactions_type', 'type'),
    )

class SystemSettings(Base):
    """System-wide settings and configuration."""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)  # can be accessed by partners
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_system_settings_key', 'key'),
    )

class PartnerApplication(Base):
    """Partner registration applications."""
    __tablename__ = "partner_applications"
    
    id = Column(Integer, primary_key=True)
    
    # Contact info
    contact_name = Column(String(200), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    contact_email = Column(String(100))
    telegram_username = Column(String(100))
    
    # Business info
    business_name = Column(String(200), nullable=False)
    business_address = Column(Text, nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Additional details
    description = Column(Text)
    website = Column(String(200))
    instagram = Column(String(100))
    average_check = Column(Integer)
    
    # Status
    status = Column(String(20), default=PartnerStatus.PENDING)
    rejection_reason = Column(Text)
    processed_at = Column(DateTime)
    partner_id = Column(Integer, ForeignKey("partners.id"))  # if approved
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    city = relationship("City")
    category = relationship("Category")
    partner = relationship("Partner")

class SystemSettings(Base):
    """System-wide settings."""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database triggers and functions will be created via Alembic migrations
