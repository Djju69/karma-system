"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-08-21 12:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create cities table
    op.create_table('cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('name_ru', sa.String(length=100), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_vi', sa.String(length=100), nullable=False),
        sa.Column('name_ko', sa.String(length=100), nullable=False),
        sa.Column('lat', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('lng', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('coverage_area', Geography('POLYGON'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_cities_active', 'cities', ['is_active'], unique=False)
    op.create_index('idx_cities_default', 'cities', ['is_default'], unique=False)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tg_id', sa.String(length=20), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('lang', sa.String(length=10), nullable=True),
        sa.Column('city_id', sa.Integer(), nullable=True),
        sa.Column('policy_accepted', sa.Boolean(), nullable=True),
        sa.Column('blocked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tg_id')
    )
    op.create_index('idx_users_role', 'users', ['role'], unique=False)
    op.create_index('idx_users_tg_id', 'users', ['tg_id'], unique=False)

    # Create partner_profiles table
    op.create_table('partner_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('phone_hash', sa.String(length=64), nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notify', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create partner_auth table
    op.create_table('partner_auth',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('user_id')
    )

    # Create listings table
    op.create_table('listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('partner_profile_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('sub_slug', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('gmaps_url', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('brand_logo_url', sa.String(length=500), nullable=True),
        sa.Column('moderation_status', sa.String(length=20), nullable=True),
        sa.Column('priority_level', sa.Integer(), nullable=True),
        sa.Column('priority_until', sa.DateTime(), nullable=True),
        sa.Column('is_hidden', sa.Boolean(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
        sa.ForeignKeyConstraint(['partner_profile_id'], ['partner_profiles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_listings_city_category_status', 'listings', ['city_id', 'category', 'moderation_status'], unique=False)
    op.create_index('idx_listings_priority', 'listings', ['priority_level'], unique=False)
    op.create_index('idx_listings_user', 'listings', ['user_id'], unique=False)

    # Create qr_issues table
    op.create_table('qr_issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=36), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('issued_by_user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('redeemed_at', sa.DateTime(), nullable=True),
        sa.Column('redeemed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['issued_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ),
        sa.ForeignKeyConstraint(['redeemed_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti')
    )
    op.create_index('idx_qr_issues_expires', 'qr_issues', ['expires_at'], unique=False)
    op.create_index('idx_qr_issues_jti', 'qr_issues', ['jti'], unique=False)
    op.create_index('idx_qr_issues_listing_status', 'qr_issues', ['listing_id', 'status'], unique=False)

    # Create partner_applications table
    op.create_table('partner_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_name', sa.String(length=100), nullable=False),
        sa.Column('contact_phone', sa.String(length=64), nullable=False),
        sa.Column('contact_email', sa.String(length=100), nullable=True),
        sa.Column('telegram_username', sa.String(length=100), nullable=True),
        sa.Column('business_name', sa.String(length=200), nullable=False),
        sa.Column('business_address', sa.Text(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('instagram', sa.String(length=100), nullable=True),
        sa.Column('average_check', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('partner_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
        sa.ForeignKeyConstraint(['partner_id'], ['partner_profiles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_partner_applications_city', 'partner_applications', ['city_id'], unique=False)
    op.create_index('idx_partner_applications_status', 'partner_applications', ['status'], unique=False)

    # Create system_settings table
    op.create_table('system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('idx_system_settings_key', 'system_settings', ['key'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_system_settings_key', table_name='system_settings')
    op.drop_table('system_settings')
    op.drop_index('idx_partner_applications_status', table_name='partner_applications')
    op.drop_index('idx_partner_applications_city', table_name='partner_applications')
    op.drop_table('partner_applications')
    op.drop_index('idx_qr_issues_listing_status', table_name='qr_issues')
    op.drop_index('idx_qr_issues_jti', table_name='qr_issues')
    op.drop_index('idx_qr_issues_expires', table_name='qr_issues')
    op.drop_table('qr_issues')
    op.drop_index('idx_listings_user', table_name='listings')
    op.drop_index('idx_listings_priority', table_name='listings')
    op.drop_index('idx_listings_city_category_status', table_name='listings')
    op.drop_table('listings')
    op.drop_table('partner_auth')
    op.drop_table('partner_profiles')
    op.drop_index('idx_users_tg_id', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_table('users')
    op.drop_index('idx_cities_default', table_name='cities')
    op.drop_index('idx_cities_active', table_name='cities')
    op.drop_table('cities')
