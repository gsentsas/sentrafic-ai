"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('admin', 'operator', 'viewer', name='userrole'), nullable=False, server_default='viewer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # --- sites ---
    op.create_table(
        'sites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('address', sa.String(255), nullable=False, server_default=''),
        sa.Column('city', sa.String(255), nullable=False, server_default=''),
        sa.Column('latitude', sa.Float(), nullable=False, server_default='0'),
        sa.Column('longitude', sa.Float(), nullable=False, server_default='0'),
        sa.Column('site_type', sa.Enum(
            'intersection', 'highway', 'parking', 'logistics', 'bus_station', 'industrial',
            name='sitetype'
        ), nullable=False, server_default='intersection'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sites_name', 'sites', ['name'])
    op.create_index('ix_sites_slug', 'sites', ['slug'], unique=True)

    # --- cameras ---
    op.create_table(
        'cameras',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('site_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('stream_url', sa.String(1024), nullable=False),
        sa.Column('status', sa.Enum('online', 'offline', 'error', name='camerastatus'), nullable=False, server_default='offline'),
        sa.Column('location_description', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cameras_site_id', 'cameras', ['site_id'])

    # --- traffic_aggregates ---
    op.create_table(
        'traffic_aggregates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('period_seconds', sa.Integer(), nullable=False),
        sa.Column('car_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('bus_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('truck_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('motorcycle_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('person_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_occupancy', sa.Float(), nullable=True, server_default='0'),
        sa.Column('congestion_level', sa.Enum('free', 'moderate', 'heavy', 'blocked', name='congestionlevel'), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_traffic_aggregates_camera_id', 'traffic_aggregates', ['camera_id'])
    op.create_index('ix_traffic_aggregates_timestamp', 'traffic_aggregates', ['timestamp'])

    # --- alerts ---
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('site_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_type', sa.Enum(
            'congestion', 'stopped_vehicle', 'camera_offline', 'no_recent_data',
            'abnormal_low_traffic', 'abnormal_high_traffic', 'zone_overflow',
            name='alerttype'
        ), nullable=False),
        sa.Column('severity', sa.Enum('info', 'warning', 'critical', name='alertseverity'), nullable=False, server_default='warning'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_alerts_camera_id', 'alerts', ['camera_id'])
    op.create_index('ix_alerts_is_resolved', 'alerts', ['is_resolved'])
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'])

    # --- camera_health_checks ---
    op.create_table(
        'camera_health_checks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('ok', 'degraded', 'offline', name='healthstatus'), nullable=False),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('last_frame_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_camera_health_checks_camera_id', 'camera_health_checks', ['camera_id'])
    op.create_index('ix_camera_health_checks_checked_at', 'camera_health_checks', ['checked_at'])


def downgrade() -> None:
    op.drop_table('camera_health_checks')
    op.drop_table('alerts')
    op.drop_table('traffic_aggregates')
    op.drop_table('cameras')
    op.drop_table('sites')
    op.drop_table('users')
    # Drop enums
    op.execute('DROP TYPE IF EXISTS alertseverity')
    op.execute('DROP TYPE IF EXISTS alerttype')
    op.execute('DROP TYPE IF EXISTS congestionlevel')
    op.execute('DROP TYPE IF EXISTS camerastatus')
    op.execute('DROP TYPE IF EXISTS healthstatus')
    op.execute('DROP TYPE IF EXISTS sitetype')
    op.execute('DROP TYPE IF EXISTS userrole')
