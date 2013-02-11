from lxml import etree
import model
from datetime import datetime
import iso8601
from iatilib import session

# ===========
# Main method
# ===========
def parse(xml_string):
    xml = etree.fromstring(xml_string)
    logger = Logger()
    activity = model.Activity._parse_xml(logger, xml)
    _validate(logger,activity)
    return activity,logger.errors

# =========
# Utilities
# =========
class Logger():
    def __init__(self):
        self.errors = []
    def log(self,text,level='warning'):
        level = { 'warning': 1, 'error' : 2 }[level]
        self.errors.append( model.LogError(text=unicode(text),level=level) )

def _parse_float(logger,x):
    if x is None or x.strip()=='': return 0.0
    x = x.replace(',','')
    try:
        return float(x)
    except ValueError, e:
        logger.log(unicode(e))
        return 0

def _parse_int(logger,x):
    if x is None or x.strip()=='': return 0
    x = x.replace(',','')
    try:
        return int(x)
    except ValueError, e:
        logger.log(unicode(e))
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

