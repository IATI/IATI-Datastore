import json
import re

def _field(x):
    if x['item']=='': return ''
    name = x['xml'].strip()
    assert not '_' in name
    name = name.replace('xml:lang','lang')
    name = name.replace('-','_')
    name = name.replace('/','__')
    name = name.replace('@','')
    name = name.replace('()','')
    assert re.match(r'^[A-Za-z0-9_]+$',name),name
    assert len(name), x
    typenames = {
            '' : 'UnicodeText',
            'mixed' : 'UnicodeText',
            'Text' : 'UnicodeText',
            'Decimal'  : 'Float',
            'Integer'  : 'Float',
            'xsd:int'  : 'Float',
            'xsd:integer'  : 'Float',
            'xsd:NMTOKEN'  : 'UnicodeText',
            'Boolean'  : 'Boolean',
            'xsd:anyURI'  : 'UnicodeText',
            'DateTime'  : 'DateTime',
            }
    typename = typenames[ x['format'] ]
    return '%s = Column(%s)' % (name,typename)

def _class(filename,classname,tablename):
    with open(filename,'r') as f:
        data = json.load(f)
    code = [ _field(x) for x in data ]
    code = filter(bool,code)
    code = ['class %s:'%classname,
            '    __tablename__ = \'%s\'' % tablename,
            '    id = Column(Integer, primary_key=True)',
            '    parent_resource = Column(UnicodeText, ForeignKey(\'indexed_resource.id\'), nullable=False)'
            ] + [ '    '+x for x in code ]
    return code

def main():
    for x in _class('spec-activity.json','Activity','activity'):
        print x

if __name__=='__main__':
    main()
