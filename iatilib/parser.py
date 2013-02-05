from lxml import etree
import model
from . import log
from datetime import datetime
import iso8601

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
            # Parse first...
            activity = model.Activity._parse_xml(logger, xml)
            transactions   = [ model.Transaction._parse_xml(logger,x) for x in xml.findall('transaction') ]
            sectors        = [ model.Sector._parse_xml(logger,x) for x in xml.findall('sector') ]
            activitydates  = [ model.ActivityDate._parse_xml(logger,x) for x in xml.findall('activity-date') ]
            contactinfos   = [ model.ContactInfo._parse_xml(logger,x) for x in xml.findall('contact-info') ]
            participatings = [ model.ParticipatingOrg._parse_xml(logger,x) for x in xml.findall('participating-org') ]
            # .. then update the global object set
            all_objects.append(activity)
            all_objects.extend(transactions)
            all_objects.extend(sectors)
            all_objects.extend(activitydates)
            all_objects.extend(contactinfos)
            all_objects.extend(participatings)
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
    return iso8601.parse_date(x)

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

