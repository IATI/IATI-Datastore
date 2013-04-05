"""Add recepient-region_code

Revision ID: ce28b6ebf50
Revises: 51b25ce2c36a
Create Date: 2013-04-05 17:37:03.282473

"""

# revision identifiers, used by Alembic.
revision = 'ce28b6ebf50'
down_revision = '51b25ce2c36a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


def upgrade():
    enum = ENUM(
        u'289', u'619', u'679', u'889', u'789', u'998', u'589', u'380', u'798', u'689', u'89', u'498', u'489', u'389', u'189', u'298',
        name="ck_region",
        create_type=False
    )
    enum.create(op.get_bind(), checkfirst=False)
    op.create_table(
        'region_percentage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('percentage', sa.Integer(), nullable=True),
        sa.Column('region', enum, nullable=False),
        sa.Column('activity_id', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activity.iati_identifier'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('region_percentage')
    ENUM(name="ck_region").drop(op.get_bind(), checkfirst=False)
