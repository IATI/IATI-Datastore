"""Add reporting-org_type

Revision ID: 51b25ce2c36a
Revises: 20cb50f50e35
Create Date: 2013-04-05 16:23:28.672261

"""

# revision identifiers, used by Alembic.
revision = '51b25ce2c36a'
down_revision = '20cb50f50e35'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


def upgrade():
    enum = ENUM(
        u'10', u'15', u'21', u'22', u'23', u'30', u'40', u'60', u'70', u'80',
        name="ck_organisation_type",
        create_type=False
    )
    enum.create(op.get_bind(), checkfirst=False)
    op.add_column('organisation', sa.Column('type', enum, nullable=True))


def downgrade():
    op.drop_column('organisation', 'type')
    ENUM(name="ck_organisation_type").drop(op.get_bind(), checkfirst=False)
