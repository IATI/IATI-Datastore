from lxml import etree
from model import *
from . import log
from datetime import datetime

# ===========
# Main method
# ===========
def parse(url):
    """Read an IATI-XML file and return a set of objects.
    Or throw XML parse errors. Whatever."""
    parser = etree.XMLParser(ns_clean=True, recover=True)
    doc = etree.parse(url, parser)
    all_objects = []
    logger = Logger('parse(\'%s\'): '%url)
    for xml in doc.findall("iati-activity"):
        try:
            activity = _parse_activity(logger, xml)
            transactions = [ _parse_transaction(logger,x) for x in xml.findall('transaction') ]
            all_objects.append(activity)
            all_objects.extend(transactions)
        except ParseError as e:
            logger.log(str(e))
        except (ValueError,AssertionError) as e:
            logger.log(str(e),level='error')
    return all_objects

# =========
# Utilities
# =========
class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Logger():
    def __init__(self, prefix):
        self.prefix = prefix
    def log(self,string,level='warning'):
        log(level,self.prefix+string)

def _parse_float(x):
    if x is None: return 0.0
    x = x.replace(',','')
    return float(x)

def _parse_datetime(x):
    return datetime.now()

def _parse_boolean(x):
    if x is None: return False
    x = x.lower().strip()
    if x=='true': return True
    if x=='false': return False
    raise ParseError('Expected boolean True/False; got %s' % x)

def _nav(logger, element, path, attrib=None, text=False, parser=None):
    assert text==True or (attrib is not None)
    for x in path:
        subelement = element.findall(x)
        if len(subelement)==0: return None
        if len(subelement)>1:
            logger.log('Found multiple %s in path %s' % (x,'/'.join(path)))
        element = subelement[0]
    if text:
        out = element.text
    else:
        out = element.attrib.get(attrib) 
    if out is not None:
        out = unicode(out).strip()
    if parser is not None:
        out = parser(out)
    return out


# =============================================================
# ========   Everything below is code-generated!   ============
# ========   See /spec for how it's made.          ============
# =============================================================
# ==  eg. (1) delete everything below                        ==
# ==      (2) put your cursor down there                     ==
# ==      (3) execute vim command:                           ==
# ==          :r ! python spec/codegen.py parser             ==
# =============================================================
def _parse_activity(logger,xml):
    data = {}
    # @version
    data['version'] = _nav(logger, xml, [], attrib='version', parser=_parse_float)
    # @last-updated-datetime
    data['last_updated_datetime'] = _nav(logger, xml, [], attrib='last-updated-datetime', parser=_parse_datetime)
    # @xml:lang
    data['lang'] = _nav(logger, xml, [], attrib='xml:lang')
    # @default-currency
    data['default_currency'] = _nav(logger, xml, [], attrib='default-currency')
    # @hierarchy
    data['hierarchy'] = _nav(logger, xml, [], attrib='hierarchy', parser=_parse_float)
    # @linked-data-uri
    data['linked_data_uri'] = _nav(logger, xml, [], attrib='linked-data-uri')
    # activity-website/text()
    data['activity_website__text'] = _nav(logger, xml, ['activity-website'], text=True)
    # reporting-org/text()
    data['reporting_org__text'] = _nav(logger, xml, ['reporting-org'], text=True)
    # reporting-org/@ref
    data['reporting_org__ref'] = _nav(logger, xml, ['reporting-org'], attrib='ref')
    # reporting-org/@type
    data['reporting_org__type'] = _nav(logger, xml, ['reporting-org'], attrib='type')
    # reporting-org/@xml:lang
    data['reporting_org__lang'] = _nav(logger, xml, ['reporting-org'], attrib='xml:lang')
    # participating-org/text()
    data['participating_org__text'] = _nav(logger, xml, ['participating-org'], text=True)
    # participating-org/@ref
    data['participating_org__ref'] = _nav(logger, xml, ['participating-org'], attrib='ref')
    # participating-org/@type
    data['participating_org__type'] = _nav(logger, xml, ['participating-org'], attrib='type')
    # participating-org/@role
    data['participating_org__role'] = _nav(logger, xml, ['participating-org'], attrib='role')
    # participating-org/@xml:lang
    data['participating_org__lang'] = _nav(logger, xml, ['participating-org'], attrib='xml:lang')
    # recipient-country/text()
    data['recipient_country__text'] = _nav(logger, xml, ['recipient-country'], text=True)
    # recipient-country/@code
    data['recipient_country__code'] = _nav(logger, xml, ['recipient-country'], attrib='code')
    # recipient-country/@percentage
    data['recipient_country__percentage'] = _nav(logger, xml, ['recipient-country'], attrib='percentage', parser=_parse_float)
    # recipient-country/@xml:lang
    data['recipient_country__lang'] = _nav(logger, xml, ['recipient-country'], attrib='xml:lang')
    # recipient-region/text()
    data['recipient_region__text'] = _nav(logger, xml, ['recipient-region'], text=True)
    # recipient-region/@code
    data['recipient_region__code'] = _nav(logger, xml, ['recipient-region'], attrib='code')
    # recipient-region/@percentage
    data['recipient_region__percentage'] = _nav(logger, xml, ['recipient-region'], attrib='percentage', parser=_parse_float)
    # recipient-region/@xml:lang
    data['recipient_region__lang'] = _nav(logger, xml, ['recipient-region'], attrib='xml:lang')
    # collaboration-type/text()
    data['collaboration_type__text'] = _nav(logger, xml, ['collaboration-type'], text=True)
    # collaboration-type/@code
    data['collaboration_type__code'] = _nav(logger, xml, ['collaboration-type'], attrib='code')
    # collaboration-type/@xml:lang
    data['collaboration_type__lang'] = _nav(logger, xml, ['collaboration-type'], attrib='xml:lang')
    # default-flow-type/text()
    data['default_flow_type__text'] = _nav(logger, xml, ['default-flow-type'], text=True)
    # default-flow-type/@code
    data['default_flow_type__code'] = _nav(logger, xml, ['default-flow-type'], attrib='code')
    # default-flow-type/@xml:lang
    data['default_flow_type__lang'] = _nav(logger, xml, ['default-flow-type'], attrib='xml:lang')
    # default-aid-type/text()
    data['default_aid_type__text'] = _nav(logger, xml, ['default-aid-type'], text=True)
    # default-aid-type/@code
    data['default_aid_type__code'] = _nav(logger, xml, ['default-aid-type'], attrib='code')
    # default-aid-type/@xml:lang
    data['default_aid_type__lang'] = _nav(logger, xml, ['default-aid-type'], attrib='xml:lang')
    # default-finance-type/text()
    data['default_finance_type__text'] = _nav(logger, xml, ['default-finance-type'], text=True)
    # default-finance-type/@code
    data['default_finance_type__code'] = _nav(logger, xml, ['default-finance-type'], attrib='code')
    # default-finance-type/@xml:lang
    data['default_finance_type__lang'] = _nav(logger, xml, ['default-finance-type'], attrib='xml:lang')
    # iati-identifier/text()
    data['iati_identifier__text'] = _nav(logger, xml, ['iati-identifier'], text=True)
    # other-identifier/text()
    data['other_identifier__text'] = _nav(logger, xml, ['other-identifier'], text=True)
    # other-identifier/@owner-ref
    data['other_identifier__owner_ref'] = _nav(logger, xml, ['other-identifier'], attrib='owner-ref')
    # other-identifier/@owner-name
    data['other_identifier__owner_name'] = _nav(logger, xml, ['other-identifier'], attrib='owner-name')
    # title/text()
    data['title__text'] = _nav(logger, xml, ['title'], text=True)
    # title/@xml:lang
    data['title__lang'] = _nav(logger, xml, ['title'], attrib='xml:lang')
    # description/text()
    data['description__text'] = _nav(logger, xml, ['description'], text=True)
    # description/@type
    data['description__type'] = _nav(logger, xml, ['description'], attrib='type')
    # description/@xml:lang
    data['description__lang'] = _nav(logger, xml, ['description'], attrib='xml:lang')
    # sector/text()
    data['sector__text'] = _nav(logger, xml, ['sector'], text=True)
    # sector/@code
    data['sector__code'] = _nav(logger, xml, ['sector'], attrib='code')
    # sector/@vocabulary
    data['sector__vocabulary'] = _nav(logger, xml, ['sector'], attrib='vocabulary')
    # sector/@percentage
    data['sector__percentage'] = _nav(logger, xml, ['sector'], attrib='percentage', parser=_parse_float)
    # sector/@xml:lang
    data['sector__lang'] = _nav(logger, xml, ['sector'], attrib='xml:lang')
    # activity-date/text()
    data['activity_date__text'] = _nav(logger, xml, ['activity-date'], text=True)
    # activity-date/@type
    data['activity_date__type'] = _nav(logger, xml, ['activity-date'], attrib='type')
    # activity-date/@iso-date
    data['activity_date__iso_date'] = _nav(logger, xml, ['activity-date'], attrib='iso-date')
    # activity-date/@xml:lang
    data['activity_date__lang'] = _nav(logger, xml, ['activity-date'], attrib='xml:lang')
    # activity-status/text()
    data['activity_status__text'] = _nav(logger, xml, ['activity-status'], text=True)
    # activity-status/@code
    data['activity_status__code'] = _nav(logger, xml, ['activity-status'], attrib='code')
    # activity-status/@xml:lang
    data['activity_status__lang'] = _nav(logger, xml, ['activity-status'], attrib='xml:lang')
    # contact-info/organisation/text()
    data['contact_info__organisation__text'] = _nav(logger, xml, ['contact-info','organisation'], text=True)
    # contact-info/person-name/text()
    data['contact_info__person_name__text'] = _nav(logger, xml, ['contact-info','person-name'], text=True)
    # contact-info/telephone/text()
    data['contact_info__telephone__text'] = _nav(logger, xml, ['contact-info','telephone'], text=True)
    # contact-info/email/text()
    data['contact_info__email__text'] = _nav(logger, xml, ['contact-info','email'], text=True)
    # contact-info/mailing-address/text()
    data['contact_info__mailing_address__text'] = _nav(logger, xml, ['contact-info','mailing-address'], text=True)
    # default-tied-status/text()
    data['default_tied_status__text'] = _nav(logger, xml, ['default-tied-status'], text=True)
    # default-tied-status/@code
    data['default_tied_status__code'] = _nav(logger, xml, ['default-tied-status'], attrib='code')
    # default-tied-status/@xml:lang
    data['default_tied_status__lang'] = _nav(logger, xml, ['default-tied-status'], attrib='xml:lang')
    # policy-marker/text()
    data['policy_marker__text'] = _nav(logger, xml, ['policy-marker'], text=True)
    # policy-marker/@code
    data['policy_marker__code'] = _nav(logger, xml, ['policy-marker'], attrib='code')
    # policy-marker/@vocabulary
    data['policy_marker__vocabulary'] = _nav(logger, xml, ['policy-marker'], attrib='vocabulary')
    # policy-marker/@significance
    data['policy_marker__significance'] = _nav(logger, xml, ['policy-marker'], attrib='significance')
    # policy-marker/@xml:lang
    data['policy_marker__lang'] = _nav(logger, xml, ['policy-marker'], attrib='xml:lang')
    # location/@percentage
    data['location__percentage'] = _nav(logger, xml, ['location'], attrib='percentage', parser=_parse_float)
    # location/location-type/text()
    data['location__location_type__text'] = _nav(logger, xml, ['location','location-type'], text=True)
    # location/location-type/@code
    data['location__location_type__code'] = _nav(logger, xml, ['location','location-type'], attrib='code')
    # location/location-type/@xml:lang
    data['location__location_type__lang'] = _nav(logger, xml, ['location','location-type'], attrib='xml:lang')
    # location/name/text()
    data['location__name__text'] = _nav(logger, xml, ['location','name'], text=True)
    # location/name/@xml:lang
    data['location__name__lang'] = _nav(logger, xml, ['location','name'], attrib='xml:lang')
    # location/description/text()
    data['location__description__text'] = _nav(logger, xml, ['location','description'], text=True)
    # location/description/@xml:lang
    data['location__description__lang'] = _nav(logger, xml, ['location','description'], attrib='xml:lang')
    # location/administrative/text()
    data['location__administrative__text'] = _nav(logger, xml, ['location','administrative'], text=True)
    # location/administrative/@country
    data['location__administrative__country'] = _nav(logger, xml, ['location','administrative'], attrib='country')
    # location/administrative/@adm1
    data['location__administrative__adm1'] = _nav(logger, xml, ['location','administrative'], attrib='adm1')
    # location/administrative/@adm2
    data['location__administrative__adm2'] = _nav(logger, xml, ['location','administrative'], attrib='adm2')
    # location/coordinates/@latitude
    data['location__coordinates__latitude'] = _nav(logger, xml, ['location','coordinates'], attrib='latitude', parser=_parse_float)
    # location/coordinates/@longitude
    data['location__coordinates__longitude'] = _nav(logger, xml, ['location','coordinates'], attrib='longitude', parser=_parse_float)
    # location/coordinates/@precision
    data['location__coordinates__precision'] = _nav(logger, xml, ['location','coordinates'], attrib='precision')
    # location/gazetteer-entry/text()
    data['location__gazetteer_entry__text'] = _nav(logger, xml, ['location','gazetteer-entry'], text=True)
    # location/gazetteer-entry/@gazetteer-ref
    data['location__gazetteer_entry__gazetteer_ref'] = _nav(logger, xml, ['location','gazetteer-entry'], attrib='gazetteer-ref')
    # result/@type
    data['result__type'] = _nav(logger, xml, ['result'], attrib='type')
    # result/@aggregation-status
    data['result__aggregation_status'] = _nav(logger, xml, ['result'], attrib='aggregation-status', parser=_parse_boolean)
    # result/title/text()
    data['result__title__text'] = _nav(logger, xml, ['result','title'], text=True)
    # result/title/@xml:lang
    data['result__title__lang'] = _nav(logger, xml, ['result','title'], attrib='xml:lang')
    # result/description/text()
    data['result__description__text'] = _nav(logger, xml, ['result','description'], text=True)
    # result/description/@type
    data['result__description__type'] = _nav(logger, xml, ['result','description'], attrib='type')
    # result/description/@xml:lang
    data['result__description__lang'] = _nav(logger, xml, ['result','description'], attrib='xml:lang')
    # result/indicator/@measure
    data['result__indicator__measure'] = _nav(logger, xml, ['result','indicator'], attrib='measure')
    # result/indicator/@ascending
    data['result__indicator__ascending'] = _nav(logger, xml, ['result','indicator'], attrib='ascending', parser=_parse_boolean)
    # result/indicator/title/text()
    data['result__indicator__title__text'] = _nav(logger, xml, ['result','indicator','title'], text=True)
    # result/indicator/title/@xml:lang
    data['result__indicator__title__lang'] = _nav(logger, xml, ['result','indicator','title'], attrib='xml:lang')
    # result/indicator/description/text()
    data['result__indicator__description__text'] = _nav(logger, xml, ['result','indicator','description'], text=True)
    # result/indicator/description/@type
    data['result__indicator__description__type'] = _nav(logger, xml, ['result','indicator','description'], attrib='type')
    # result/indicator/description/@xml:lang
    data['result__indicator__description__lang'] = _nav(logger, xml, ['result','indicator','description'], attrib='xml:lang')
    # result/indicator/baseline/@year
    data['result__indicator__baseline__year'] = _nav(logger, xml, ['result','indicator','baseline'], attrib='year', parser=_parse_float)
    # result/indicator/baseline/@value
    data['result__indicator__baseline__value'] = _nav(logger, xml, ['result','indicator','baseline'], attrib='value')
    # result/indicator/baseline/comment/text()
    data['result__indicator__baseline__comment__text'] = _nav(logger, xml, ['result','indicator','baseline','comment'], text=True)
    # result/indicator/baseline/comment/@xml:lang
    data['result__indicator__baseline__comment__lang'] = _nav(logger, xml, ['result','indicator','baseline','comment'], attrib='xml:lang')
    # result/indicator/period/period-start/text()
    data['result__indicator__period__period_start__text'] = _nav(logger, xml, ['result','indicator','period','period-start'], text=True)
    # result/indicator/period/period-start/@iso-date
    data['result__indicator__period__period_start__iso_date'] = _nav(logger, xml, ['result','indicator','period','period-start'], attrib='iso-date')
    # result/indicator/period/period-end/text()
    data['result__indicator__period__period_end__text'] = _nav(logger, xml, ['result','indicator','period','period-end'], text=True)
    # result/indicator/period/period-end/@iso-date
    data['result__indicator__period__period_end__iso_date'] = _nav(logger, xml, ['result','indicator','period','period-end'], attrib='iso-date')
    # result/indicator/period/target/@value
    data['result__indicator__period__target__value'] = _nav(logger, xml, ['result','indicator','period','target'], attrib='value')
    # result/indicator/period/target/comment/text()
    data['result__indicator__period__target__comment__text'] = _nav(logger, xml, ['result','indicator','period','target','comment'], text=True)
    # result/indicator/period/target/comment/@xml:lang
    data['result__indicator__period__target__comment__lang'] = _nav(logger, xml, ['result','indicator','period','target','comment'], attrib='xml:lang')
    # result/indicator/period/actual/@value
    data['result__indicator__period__actual__value'] = _nav(logger, xml, ['result','indicator','period','actual'], attrib='value')
    # result/indicator/period/actual/comment/text()
    data['result__indicator__period__actual__comment__text'] = _nav(logger, xml, ['result','indicator','period','actual','comment'], text=True)
    # result/indicator/period/actual/comment/@xml:lang
    data['result__indicator__period__actual__comment__lang'] = _nav(logger, xml, ['result','indicator','period','actual','comment'], attrib='xml:lang')
    # conditions/@attached
    data['conditions__attached'] = _nav(logger, xml, ['conditions'], attrib='attached', parser=_parse_boolean)
    # conditions/condition/text()
    data['conditions__condition__text'] = _nav(logger, xml, ['conditions','condition'], text=True)
    # conditions/condition/@type
    data['conditions__condition__type'] = _nav(logger, xml, ['conditions','condition'], attrib='type')
    # budget/@type
    data['budget__type'] = _nav(logger, xml, ['budget'], attrib='type')
    # budget/period-start/text()
    data['budget__period_start__text'] = _nav(logger, xml, ['budget','period-start'], text=True)
    # budget/period-start/@iso-date
    data['budget__period_start__iso_date'] = _nav(logger, xml, ['budget','period-start'], attrib='iso-date')
    # budget/period-end/text()
    data['budget__period_end__text'] = _nav(logger, xml, ['budget','period-end'], text=True)
    # budget/period-end/@iso-date
    data['budget__period_end__iso_date'] = _nav(logger, xml, ['budget','period-end'], attrib='iso-date')
    # budget/value/text()
    data['budget__value__text'] = _nav(logger, xml, ['budget','value'], text=True, parser=_parse_float)
    # budget/value/@currency
    data['budget__value__currency'] = _nav(logger, xml, ['budget','value'], attrib='currency')
    # budget/value/@value-date
    data['budget__value__value_date'] = _nav(logger, xml, ['budget','value'], attrib='value-date')
    # planned-disbursement/@updated
    data['planned_disbursement__updated'] = _nav(logger, xml, ['planned-disbursement'], attrib='updated')
    # planned-disbursement/period-start/text()
    data['planned_disbursement__period_start__text'] = _nav(logger, xml, ['planned-disbursement','period-start'], text=True)
    # planned-disbursement/period-start/@iso-date
    data['planned_disbursement__period_start__iso_date'] = _nav(logger, xml, ['planned-disbursement','period-start'], attrib='iso-date')
    # planned-disbursement/period-end/text()
    data['planned_disbursement__period_end__text'] = _nav(logger, xml, ['planned-disbursement','period-end'], text=True)
    # planned-disbursement/period-end/@iso-date
    data['planned_disbursement__period_end__iso_date'] = _nav(logger, xml, ['planned-disbursement','period-end'], attrib='iso-date')
    # planned-disbursement/value/text()
    data['planned_disbursement__value__text'] = _nav(logger, xml, ['planned-disbursement','value'], text=True, parser=_parse_float)
    # planned-disbursement/value/@currency
    data['planned_disbursement__value__currency'] = _nav(logger, xml, ['planned-disbursement','value'], attrib='currency')
    # planned-disbursement/value/@value-date
    data['planned_disbursement__value__value_date'] = _nav(logger, xml, ['planned-disbursement','value'], attrib='value-date')
    # related-activity/text()
    data['related_activity__text'] = _nav(logger, xml, ['related-activity'], text=True)
    # related-activity/@ref
    data['related_activity__ref'] = _nav(logger, xml, ['related-activity'], attrib='ref')
    # related-activity/@type
    data['related_activity__type'] = _nav(logger, xml, ['related-activity'], attrib='type')
    # related-activity/@xml:lang
    data['related_activity__lang'] = _nav(logger, xml, ['related-activity'], attrib='xml:lang')
    # document-link/@url
    data['document_link__url'] = _nav(logger, xml, ['document-link'], attrib='url')
    # document-link/@format
    data['document_link__format'] = _nav(logger, xml, ['document-link'], attrib='format')
    # document-link/title/text()
    data['document_link__title__text'] = _nav(logger, xml, ['document-link','title'], text=True)
    # document-link/title/@xml:lang
    data['document_link__title__lang'] = _nav(logger, xml, ['document-link','title'], attrib='xml:lang')
    # document-link/category/text()
    data['document_link__category__text'] = _nav(logger, xml, ['document-link','category'], text=True)
    # document-link/category/@code
    data['document_link__category__code'] = _nav(logger, xml, ['document-link','category'], attrib='code')
    # document-link/category/@xml:lang
    data['document_link__category__lang'] = _nav(logger, xml, ['document-link','category'], attrib='xml:lang')
    # document-link/language/text()
    data['document_link__language__text'] = _nav(logger, xml, ['document-link','language'], text=True)
    # document-link/language/@code
    data['document_link__language__code'] = _nav(logger, xml, ['document-link','language'], attrib='code')
    # document-link/language/@xml:lang
    data['document_link__language__lang'] = _nav(logger, xml, ['document-link','language'], attrib='xml:lang')
    # legacy-data/text()
    data['legacy_data__text'] = _nav(logger, xml, ['legacy-data'], text=True)
    # legacy-data/@name
    data['legacy_data__name'] = _nav(logger, xml, ['legacy-data'], attrib='name')
    # legacy-data/@value
    data['legacy_data__value'] = _nav(logger, xml, ['legacy-data'], attrib='value')
    # legacy-data/@iati-equivalent
    data['legacy_data__iati_equivalent'] = _nav(logger, xml, ['legacy-data'], attrib='iati-equivalent')
    return Activity(**data)

def _parse_transaction(logger,xml):
    data = {}
    # @ref
    data['ref'] = _nav(logger, xml, [], attrib='ref')
    # value/text()
    data['value__text'] = _nav(logger, xml, ['value'], text=True, parser=_parse_float)
    # value/@currency
    data['value__currency'] = _nav(logger, xml, ['value'], attrib='currency')
    # value/@value-date
    data['value__value_date'] = _nav(logger, xml, ['value'], attrib='value-date')
    # description/text()
    data['description__text'] = _nav(logger, xml, ['description'], text=True)
    # description/@xml:lang
    data['description__lang'] = _nav(logger, xml, ['description'], attrib='xml:lang')
    # transaction-type/text()
    data['transaction_type__text'] = _nav(logger, xml, ['transaction-type'], text=True)
    # transaction-type/@code
    data['transaction_type__code'] = _nav(logger, xml, ['transaction-type'], attrib='code')
    # transaction-type/@xml:lang
    data['transaction_type__lang'] = _nav(logger, xml, ['transaction-type'], attrib='xml:lang')
    # provider-org/text()
    data['provider_org__text'] = _nav(logger, xml, ['provider-org'], text=True)
    # provider-org/@ref
    data['provider_org__ref'] = _nav(logger, xml, ['provider-org'], attrib='ref')
    # provider-org/@provider-activity-id
    data['provider_org__provider_activity_id'] = _nav(logger, xml, ['provider-org'], attrib='provider-activity-id')
    # receiver-org/text()
    data['receiver_org__text'] = _nav(logger, xml, ['receiver-org'], text=True)
    # receiver-org/@ref
    data['receiver_org__ref'] = _nav(logger, xml, ['receiver-org'], attrib='ref')
    # receiver-org/@receiver-activity-id
    data['receiver_org__receiver_activity_id'] = _nav(logger, xml, ['receiver-org'], attrib='receiver-activity-id')
    # transaction-date/text()
    data['transaction_date__text'] = _nav(logger, xml, ['transaction-date'], text=True)
    # transaction-date/@iso-date
    data['transaction_date__iso_date'] = _nav(logger, xml, ['transaction-date'], attrib='iso-date')
    # flow-type/text()
    data['flow_type__text'] = _nav(logger, xml, ['flow-type'], text=True)
    # flow-type/@code
    data['flow_type__code'] = _nav(logger, xml, ['flow-type'], attrib='code')
    # flow-type/@xml:lang
    data['flow_type__lang'] = _nav(logger, xml, ['flow-type'], attrib='xml:lang')
    # aid-type/text()
    data['aid_type__text'] = _nav(logger, xml, ['aid-type'], text=True)
    # aid-type/@code
    data['aid_type__code'] = _nav(logger, xml, ['aid-type'], attrib='code')
    # aid-type/@xml:lang
    data['aid_type__lang'] = _nav(logger, xml, ['aid-type'], attrib='xml:lang')
    # finance-type/text()
    data['finance_type__text'] = _nav(logger, xml, ['finance-type'], text=True)
    # finance-type/@code
    data['finance_type__code'] = _nav(logger, xml, ['finance-type'], attrib='code')
    # finance-type/@xml:lang
    data['finance_type__lang'] = _nav(logger, xml, ['finance-type'], attrib='xml:lang')
    # tied-status/text()
    data['tied_status__text'] = _nav(logger, xml, ['tied-status'], text=True)
    # tied-status/@code
    data['tied_status__code'] = _nav(logger, xml, ['tied-status'], attrib='code')
    # tied-status/@xml:lang
    data['tied_status__lang'] = _nav(logger, xml, ['tied-status'], attrib='xml:lang')
    # disbursement-channel/text()
    data['disbursement_channel__text'] = _nav(logger, xml, ['disbursement-channel'], text=True)
    # disbursement-channel/@code
    data['disbursement_channel__code'] = _nav(logger, xml, ['disbursement-channel'], attrib='code')
    # disbursement-channel/@xml:lang
    data['disbursement_channel__lang'] = _nav(logger, xml, ['disbursement-channel'], attrib='xml:lang')
    return Transaction(**data)
