"""Add missing sector percentage fk index

Revision ID: 454db9beed02
Revises: 5499ebf5349b
Create Date: 2013-03-27 16:50:09.902188

"""

# revision identifiers, used by Alembic.
revision = '454db9beed02'
down_revision = '5499ebf5349b'

from alembic import op
import sqlalchemy as sa


indexes = (
    ('ix_sector_percentage_activity_fk', 'sector_percentage', 'activity_id'),
)


def upgrade():
    for name, tbl, col in indexes:
        op.create_index(name, tbl, [col])


def downgrade():
    for name, tbl, col in indexes:
        op.drop_index(name)
