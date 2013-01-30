from lxml import etree
import os
import sys
import json

NAMESPACE = '{http://www.w3.org/2001/XMLSchema}'

### =============
### XML Navigator
### =============
def _findall(element, path):
    """This shouldn't be hard but etree hates XML namespaces?"""
    for child in element.findall(NAMESPACE+path[0]):
        if len(path)==1:
            yield child
        else:
            for x in _findall(child, path[1:]):
                yield x

### =========== 
### XML Parsers
### =========== 
def _parse_complexType(element):
    """ Parse an <xml:complexType> block"""
    out = {
            'name' : element.attrib.get('name'),
            'ref_attributes' : [],
            'attributes' : []
            }
    assert out['name'] is not None
    all_attributes = list(_findall(element,['simpleContent','extension','attribute'])) \
                   + list(_findall(element,['attribute']))
    for attribute in all_attributes:
        ref = attribute.attrib.get('ref')
        if ref is not None:
            out['ref_attributes'].append( ref )
        else:
            out['attributes'].append( _parse_attribute(attribute) )
    return out
def _parse_attribute(element):
    """ Parse an <xml:attribute> block"""
    out = {
            'name': element.attrib.get('name'),
            'type': element.attrib.get('type','xsd:string'),
            'use': element.attrib.get('use'),
            }
    assert out['name'] is not None
    return out
def _parse_element(element):
    """ Parse an <xml:element> block"""
    out = {
            'name' : element.attrib.get('name'),
            'ref_elements' : [],
            'sub_elements' : [],
            'ref_attributes' : [],
            'sub_attributes' : [],
            'type': element.attrib.get('type')
            }
    assert out['name'] is not None
    for attribute in _findall(element,['complexType','attribute']):
        ref = attribute.attrib.get('ref')
        if ref is not None:
            out['ref_attributes'].append( ref )
        else:
            out['sub_attributes'].append( _parse_attribute(attribute) )
    for subelement in _findall(element, ['complexType','choice','element']):
        ref = subelement.attrib.get('ref')
        if ref is not None:
            assert subelement.attrib.get('type') is None
            out['ref_elements'].append( ref )
        else:
            out['sub_elements'].append( _parse_element(subelement) )
    return out

### ==============
### Handling Files
### ==============
def _flatten(item,top_elements,top_attributes,top_types):
    """Fix the output of _parse_element so that ref_attribute
    and ref_elements are inlined as pure elements and attributes"""
    out = {
            'name':item['name'],
            'elements':[],
            'attributes':item['sub_attributes']
            }
    # Wrangle the attributes
    if item['type'] is not None:
        x = top_types[ item['type'] ]
        for attribute in x['attributes']:
            out['attributes'].append(attribute)
        for ref in x['ref_attributes']:
            out['attributes'].append( top_attributes[ref] )
    for x in item['ref_attributes']:
        if x=='xml:lang': continue
        out['attributes'].append(top_attributes[x])
    # Wrangle the text elements
    for x in item['ref_elements']:
        src = top_elements[x]
        out['elements'].append( _flatten(src,top_elements,top_attributes,top_types) )
    for x in item['sub_elements']:
        out['elements'].append( _flatten(x,top_elements,top_attributes,top_types) )
    return out

def _spec_to_dict():
    """Interpret all XML files.
    Return a dictionary of all elements & their attributes.
    Referenced attributes/elements are flattened and inlined."""
    filenames = [
            'src/iati-common.xsd',
            'src/iati-activities-schema.xsd',
            ]
    # Extract top level attributes and elements
    top_elements = []
    top_attributes = []
    top_types = []
    for filename in filenames:
        root = etree.parse(filename)
        for x in _findall( root,['element'] ):
            top_elements.append( _parse_element(x) )
        for x in _findall( root,['attribute'] ):
            top_attributes.append( _parse_attribute(x) )
        for x in _findall( root,['complexType'] ):
            top_types.append( _parse_complexType(x) )
    # Flatten all elements
    top_elements = { x['name'] : x for x in top_elements }
    top_attributes = { x['name'] : x for x in top_attributes }
    top_types = { x['name'] : x for x in top_types }
    element_dict = { key: _flatten(value,top_elements,top_attributes,top_types) for key,value in top_elements.items() }
    return element_dict

### ==================
### Handling DB Schema
### ==================
def _iterelements(prefix,element,divider='__'):
    for sub in element['elements']:
        if len(sub['elements'])==0:
            yield prefix+sub['name']
        for x in _iterelements(prefix+sub['name']+divider,sub,divider):
            yield x
def _iterattributes(element,divider='__'):
    for attrib in element['attributes']:
        yield attrib['name']
    for sub in element['elements']:
        for x in _iterattributes(sub, divider):
            yield sub['name']+divider+x

def main():
    # Get the list of XPath elements as scraped from the website
    with open('src/from_website.json','r') as f:
        sanity_check = json.load(f)
        sanity_check = map(str,sanity_check)
    # Parse the official schema
    flat_elements = _spec_to_dict()
    activity_root = flat_elements['iati-activity']
    # Sanity checks. Have we found all elements?
    sanity_textfields = set([ x for x in sanity_check if '/text()' in x ])
    textfields = set([ x+'/text()' for x in  _iterelements('',activity_root,divider='/') ])
    for invalid in textfields-sanity_textfields:
        print >>sys.stderr,'WARNING: Schema text element not on website: %s' % invalid
    for missing in sanity_textfields-textfields:
        print >>sys.stderr,'WARNING: Website lists text element not found: %s' % missing
    # And all attribute elements?
    sanity_attribs = [ x.replace('@','') for x in sanity_check if '@' in x ]
    sanity_attribs = set(filter( lambda x:x[-8:]!='xml:lang', sanity_attribs ))
    attribfields = set(list( _iterattributes(activity_root,divider='/') ))
    for invalid in attribfields-sanity_attribs:
        print >>sys.stderr,'WARNING: Schema attribute not on website: %s' % invalid
    for missing in sanity_attribs-attribfields:
        print >>sys.stderr,'WARNING: Website lists attribute not found: %s' % missing
    # Build output
    textfields = list( _iterelements('',activity_root) )
    attribfields = list( _iterattributes(activity_root) )
    return attribfields
    return { 
            'attribfields':attribfields ,
            'textfields':textfields 
            }

### Entry point
if __name__=='__main__':
    print json.dumps( main() )
