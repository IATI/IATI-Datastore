"""Add indexes

Revision ID: 3aa6477364
Create Date: 2013-02-21 14:13:32.505089

"""

# revision identifiers, used by Alembic.
revision = '3aa6477364'
down_revision = None

from alembic import op
import sqlalchemy as sa


tables = [
    'activity',
    'activity_date',
    'activity_status',
    'budget',
    'budget_period_end',
    'budget_period_start',
    'budget_value',
    'collaborationtype',
    'condition',
    'conditions',
    'contactinfo',
    'contactinfo_email',
    'contactinfo_mail',
    'contactinfo_organisation',
    'contactinfo_person',
    'contactinfo_telephone',
    'defaultaidtype',
    'defaultfinancetype',
    'defaultflowtype',
    'defaulttiedstatus',
    'description',
    'document_link',
    'document_link_category',
    'document_link_language',
    'document_link_title',
    'iatiidentifier',
    'legacy_data',
    'location',
    'location_administrative',
    'location_coordinates',
    'location_description',
    'location_gazetteerentry',
    'location_name',
    'location_type',
    'logerror',
    'otheridentifier',
    'participatingorg',
    'planned_disbursement',
    'planned_disbursement_period_end',
    'planned_disbursement_period_start',
    'planned_disbursement_value',
    'policymarker',
    'raw_xml_blob',
    'recipientcountry',
    'recipientregion',
    'related_activity',
    'reportingorg',
    'result',
    'result_description',
    'result_indicator',
    'result_indicator_baseline',
    'result_indicator_baseline_comment',
    'result_indicator_description',
    'result_indicator_period',
    'result_indicator_period_actual',
    'result_indicator_period_actual_comment',
    'result_indicator_period_end',
    'result_indicator_period_start',
    'result_indicator_period_target',
    'result_indicator_period_target_comment',
    'result_indicator_title',
    'result_title',
    'sector',
    'title',
    'transaction',
    'transaction_aid_type',
    'transaction_date',
    'transaction_description',
    'transaction_disbursement_channel',
    'transaction_finance_type',
    'transaction_flow_type',
    'transaction_provider_org',
    'transaction_receiver_org',
    'transaction_tied_status',
    'transaction_type',
    'transaction_value',
    'activity_website'
]


def upgrade():
    for tbl in tables:
        op.create_index('ix_%s' % tbl, tbl, ['parent_id'])


def downgrade():
    for tbl in tables:
        op.drop_index('ix_%s' % tbl)
