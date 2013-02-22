"""more_fk_indexes

Revision ID: 4a468462af14
Revises: 3aa6477364
Create Date: 2013-02-22 17:12:08.772983

"""

# revision identifiers, used by Alembic.
revision = '4a468462af14'
down_revision = '3aa6477364'

from alembic import op

tables = [
    'iatiidentifier',
    'document_link',
    'policymarker',
    'defaultfinancetype',
]


def upgrade():
    for tbl in tables:
        op.create_index('ix_%s' % tbl, tbl, ['parent_id'])


def downgrade():
    for tbl in tables:
        op.drop_index('ix_%s' % tbl)
