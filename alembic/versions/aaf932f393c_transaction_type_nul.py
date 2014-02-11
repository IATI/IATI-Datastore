"""transaction type nullable

Revision ID: aaf932f393c
Revises: 187634b7caa9
Create Date: 2014-02-11 10:47:14.635465

"""

# revision identifiers, used by Alembic.
revision = 'aaf932f393c'
down_revision = '187634b7caa9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('transaction', 'type', nullable=True)


def downgrade():
    op.alter_column('transaction', 'type', nullable=False)

