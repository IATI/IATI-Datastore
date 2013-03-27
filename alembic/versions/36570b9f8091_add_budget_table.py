"""Add budget table

Revision ID: 36570b9f8091
Revises: 4dd2cc459a8
Create Date: 2013-03-14 17:17:31.245861

"""

# revision identifiers, used by Alembic.
revision = '36570b9f8091'
down_revision = '4dd2cc459a8'

from alembic import op
import sqlalchemy as sa

import sys
sys.path.append('.')

from iatilib import codelists


def upgrade():
    op.create_table(
        'budget',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Unicode(), nullable=True),
        sa.Column('type', codelists.BudgetType.db_type(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('value_amount', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activity.iati_identifier'],),
        sa.PrimaryKeyConstraint('id')
    )
    # alembic insists on trying to create the enum
    op.execute("ALTER TABLE budget ADD COLUMN value_currency ck_currency")


def downgrade():
    op.drop_table('budget')
