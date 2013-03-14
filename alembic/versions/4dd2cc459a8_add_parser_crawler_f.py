"""Add parser/crawler fields

Revision ID: 4dd2cc459a8
Revises: 1c0c431c5703
Create Date: 2013-03-14 12:48:38.897687

"""

# revision identifiers, used by Alembic.
revision = '4dd2cc459a8'
down_revision = '1c0c431c5703'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'activity',
        sa.Column('resource_url', sa.Unicode)
    )
    op.create_index(
        'ix_activity_resource_url',
        'activity',
        ['resource_url']
    )

    op.drop_column('resource', 'document')
    op.add_column('resource', sa.Column('last_parsed', sa.DateTime))
    op.add_column('resource', sa.Column('last_parse_error', sa.Unicode))
    op.add_column('resource', sa.Column('document', sa.LargeBinary))



def downgrade():
    op.drop_column('activity', 'resource_url')
    op.drop_column('resource', 'last_parsed')
    op.drop_column('resource', 'last_parse_error')
    op.drop_column('resource', 'document')
    op.add_column(
        'resource',
        sa.Column('document', sa.UnicodeText)
    )
