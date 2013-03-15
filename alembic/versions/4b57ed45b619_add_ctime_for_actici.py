"""Add ctime for acticity

Revision ID: 4b57ed45b619
Revises: 36570b9f8091
Create Date: 2013-03-15 11:09:32.072122

"""

# revision identifiers, used by Alembic.
revision = '4b57ed45b619'
down_revision = '36570b9f8091'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'activity',
        sa.Column(
            'created',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now())
    )


def downgrade():
    op.drop_column('activity', 'created')
