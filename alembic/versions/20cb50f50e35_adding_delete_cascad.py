"""Adding delete cascades

Revision ID: 20cb50f50e35
Revises: 31d3dc10e996
Create Date: 2013-04-03 15:58:25.753427

"""

# revision identifiers, used by Alembic.
revision = '20cb50f50e35'
down_revision = '31d3dc10e996'


from alembic import op
import sqlalchemy as sa


fks = [
    ("participation_activity_identifier_fkey", "participation", ["activity_identifier"]),
    ("country_percentage_activity_id_fkey", "country_percentage", ["activity_id"]),
    ("transaction_activity_id_fkey", "transaction", ["activity_id"]),
    ("sector_percentage_activity_id_fkey", "sector_percentage", ["activity_id"]),
    ("budget_activity_id_fkey", "budget", ["activity_id"]),
    ("website_activity_id_fkey", "website", ["activity_id"]),
]


def upgrade():
    op.alter_column(
        'budget',
        u'activity_id',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    op.alter_column(
        'transaction',
        u'activity_id',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    op.alter_column(
        'sector_percentage',
        u'activity_id',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    for fkname, fktable, local_cols in fks:
        op.drop_constraint(fkname, fktable, type='foreignkey')
        op.create_foreign_key(
            fkname,
            fktable,
            "activity",
            local_cols,
            ["iati_identifier"],
            ondelete="CASCADE"
        )


def downgrade():
    op.alter_column(
        'budget',
        u'activity_id',
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    op.alter_column(
        'transaction',
        u'activity_id',
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    op.alter_column(
        'sector_percentage',
        u'activity_id',
        existing_type=sa.VARCHAR(),
        nullable=True
    )

    for fkname, fktable, local_cols in fks:
        op.drop_constraint(fkname, fktable, type='foreignkey')
        op.create_foreign_key(
            fkname,
            fktable,
            "activity",
            local_cols,
            ["iati_identifier"],
        )
