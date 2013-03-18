"""Add missing FK indexes

Revision ID: 5499ebf5349b
Revises: 4b57ed45b619
Create Date: 2013-03-18 11:34:46.298365

"""

# revision identifiers, used by Alembic.
revision = '5499ebf5349b'
down_revision = '4b57ed45b619'

from alembic import op
import sqlalchemy as sa

indexes = (
    ('ix_transaction_activity_fk', 'transaction', 'activity_id'),
    ('ix_budget_activity_fk', 'budget', 'activity_id'),
    ('ix_resource_dataset_id_fk', 'resource', 'dataset_id'),
)


def upgrade():
    for name, tbl, col in indexes:
        op.create_index(name, tbl, [col])


def downgrade():
    for name, tbl, col in indexes:
        op.drop_index(name)
