from lxml import etree
import model
from . import log
from datetime import datetime
import iso8601
from iatilib import session

# ===========
# Main method
# ===========
def parse(url):
    """Read an IATI-XML file and return a set of objects.
    Or throw XML parse errors. Whatever."""
    parser = etree.XMLParser(ns_clean=True, recover=True)
    doc = etree.parse(url, parser)
    activities = []
    logger = Logger('parse(\'%s\'): '%url)
    for xml in doc.findall("iati-activity"):
        try:
            # Parse first...
            activity = model.Activity._parse_xml(logger, xml)
            for x in xml.findall('transaction'):
                activity.transaction.append( model.Transaction._parse_xml(logger,x) )
            for x in xml.findall('sector'):
                activity.sector.append( model.Sector._parse_xml(logger,x) )
            for x in xml.findall('activity-date'):
                activity.activitydate.append( model.ActivityDate._parse_xml(logger,x) )
            for x in xml.findall('contact-info'):
                activity.contactinfo.append( model.ContactInfo._parse_xml(logger,x) )
            for x in xml.findall('participating-org'):
                activity.participatingorg.append( model.ParticipatingOrg._parse_xml(logger,x) )
            # ...then validate ...
            _validate(logger,activity)
            # .. then update the global object set
            activities.append(activity)
        except (ValueError,AssertionError) as e:
            logger.log(str(e),level='error')
    return activities

# =========
# Utilities
# =========
class Logger():
    def __init__(self, prefix):
        self.prefix = prefix
    def log(self,string,level='warning'):
        log(level,self.prefix+string)

def _parse_float(logger,x):
    if x is None or x.strip()=='': return 0.0
    x = x.replace(',','')
    try:
        return float(x)
    except ValueError, e:
        logger.log(e)
        return 0

def _parse_int(logger,x):
    if x is None or x.strip()=='': return 0
    x = x.replace(',','')
    try:
        return int(x)
    except ValueError, e:
        logger.log(e)
        return 0

def _parse_datetime(logger,x):
    if x is None or x.strip()=='': return None
    try:
        if not ':' in x:
            if not x.endswith('Z'):
                x+=' '
            x += '00:00:00'
        return iso8601.parse_date(x)
    except:
        logger.log('Could not parse ISO date "%s"' % x)
        return iso8601.parse_date('2001-01-01Z00:00:00')

def _parse_boolean(logger,x):
    if x is None or x.strip()=='': return False
    x = x.lower().strip()
    if x=='true': return True
    if x=='false': return False
    logger.log('Expected boolean True/False; got %s' % x)
    return False

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
        if attrib=='xml:lang' : attrib='{http://www.w3.org/XML/1998/namespace}lang'
        out = element.attrib.get(attrib) 
    if out is not None:
        out = unicode(out).strip()
    if parser is not None:
        out = parser(logger,out)
    return out

def _validate(logger,activity):
    valid_sectors = set([ x.code for x in session.query(model.CodelistSector) ])
    assert len(valid_sectors), 'Found no CodelistSector'
    for sector in activity.sector:
        if sector.code==0: continue
        if not (sector.code in valid_sectors):
            logger.log('Invalid sector.code="%d" (text="%s")' % (sector.code,sector.text))

