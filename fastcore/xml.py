# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/11_xml.ipynb.

# %% auto 0
__all__ = ['voids', 'FT', 'attrmap', 'valmap', 'ft', 'Html', 'Safe', 'to_xml', 'highlight', 'showtags', 'Head', 'Title', 'Meta',
           'Link', 'Style', 'Body', 'Pre', 'Code', 'Div', 'Span', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Strong',
           'Em', 'B', 'I', 'U', 'S', 'Strike', 'Sub', 'Sup', 'Hr', 'Br', 'Img', 'A', 'Nav', 'Ul', 'Ol', 'Li', 'Dl',
           'Dt', 'Dd', 'Table', 'Thead', 'Tbody', 'Tfoot', 'Tr', 'Th', 'Td', 'Caption', 'Col', 'Colgroup', 'Form',
           'Input', 'Textarea', 'Button', 'Select', 'Option', 'Label', 'Fieldset', 'Legend', 'Details', 'Summary',
           'Main', 'Header', 'Footer', 'Section', 'Article', 'Aside', 'Figure', 'Figcaption', 'Mark', 'Small', 'Iframe',
           'Object', 'Embed', 'Param', 'Video', 'Audio', 'Source', 'Canvas', 'Svg', 'Math', 'Script', 'Noscript',
           'Template', 'Slot']

# %% ../nbs/11_xml.ipynb
from .utils import *

import types,json

from dataclasses import dataclass, asdict
from typing import Mapping
from functools import partial
from html import escape

# %% ../nbs/11_xml.ipynb
class FT:
    "A 'Fast Tag' structure, containing `tag`,`children`,and `attrs`"
    def __init__(self, tag:str, cs:tuple, attrs:dict=None, void_=False, **kwargs):
        assert isinstance(cs, tuple)
        self.tag,self.children,self.attrs,self.void_ = tag,cs,attrs,void_

    def __setattr__(self, k, v):
        if k.startswith('__') or k in ('tag','children','attrs','void_'): return super().__setattr__(k,v)
        self.attrs[k.lstrip('_').replace('_', '-')] = v

    def __getattr__(self, k):
        if k.startswith('__'): raise AttributeError(k)
        return self.get(k)

    @property
    def list(self): return [self.tag,self.children,self.attrs]
    def get(self, k, default=None): return self.attrs.get(k.lstrip('_').replace('_', '-'), default)
    def __repr__(self): return f'{self.tag}({self.children},{self.attrs})'

    def __add__(self, b):
        self.children = list(self.children) + tuplify(b)
        return self
    
    def __getitem__(self, idx): return self.children[idx]
    def __iter__(self): return iter(self.children)

# %% ../nbs/11_xml.ipynb
_specials = set('@.-!~:[](){}$%^&*+=|/?<>,`')

def attrmap(o):
    if o=='_' or (_specials & set(o)): return o
    o = dict(htmlClass='class', cls='class', _class='class', klass='class',
             _for='for', fr='for', htmlFor='for').get(o, o)
    return o.lstrip('_').replace('_', '-')

# %% ../nbs/11_xml.ipynb
def valmap(o):
    if is_listy(o): return ' '.join(map(str,o)) if o else None
    if isinstance(o, dict): return '; '.join(f"{k}:{v}" for k,v in o.items()) if o else None
    return o

# %% ../nbs/11_xml.ipynb
def _flatten_tuple(tup):
    if not any(isinstance(item, tuple) for item in tup): return tup
    result = []
    for item in tup:
        if isinstance(item, tuple): result.extend(item)
        else: result.append(item)
    return tuple(result)

# %% ../nbs/11_xml.ipynb
def _preproc(c, kw, attrmap=attrmap, valmap=valmap):
    if len(c)==1 and isinstance(c[0], (types.GeneratorType, map, filter)): c = tuple(c[0])
    attrs = {attrmap(k.lower()):valmap(v) for k,v in kw.items() if v is not None}
    return _flatten_tuple(c),attrs

# %% ../nbs/11_xml.ipynb
def ft(tag:str, *c, void_:bool=False, attrmap:callable=attrmap, valmap:callable=valmap, **kw):
    "Create an `FT` structure for `to_xml()`"
    return FT(tag.lower(),*_preproc(c,kw,attrmap=attrmap, valmap=valmap), void_=void_)

# %% ../nbs/11_xml.ipynb
voids = set('area base br col command embed hr img input keygen link meta param source track wbr !doctype'.split())
_g = globals()
_all_ = ['Head', 'Title', 'Meta', 'Link', 'Style', 'Body', 'Pre', 'Code',
    'Div', 'Span', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Strong', 'Em', 'B',
    'I', 'U', 'S', 'Strike', 'Sub', 'Sup', 'Hr', 'Br', 'Img', 'A', 'Link', 'Nav',
    'Ul', 'Ol', 'Li', 'Dl', 'Dt', 'Dd', 'Table', 'Thead', 'Tbody', 'Tfoot', 'Tr',
    'Th', 'Td', 'Caption', 'Col', 'Colgroup', 'Form', 'Input', 'Textarea',
    'Button', 'Select', 'Option', 'Label', 'Fieldset', 'Legend', 'Details',
    'Summary', 'Main', 'Header', 'Footer', 'Section', 'Article', 'Aside', 'Figure',
    'Figcaption', 'Mark', 'Small', 'Iframe', 'Object', 'Embed', 'Param', 'Video',
    'Audio', 'Source', 'Canvas', 'Svg', 'Math', 'Script', 'Noscript', 'Template', 'Slot']

for o in _all_: _g[o] = partial(ft, o.lower(), void_=o.lower() in voids)

# %% ../nbs/11_xml.ipynb
def Html(*c, doctype=True, **kwargs)->FT:
    "An HTML tag, optionally preceeded by `!DOCTYPE HTML`"
    res = ft('html', *c, **kwargs)
    if not doctype: return res
    return (ft('!DOCTYPE', html=True, void_=True), res)

# %% ../nbs/11_xml.ipynb
class Safe(str):
    def __html__(self): return self

# %% ../nbs/11_xml.ipynb
def _escape(s): return '' if s is None else s.__html__() if hasattr(s, '__html__') else escape(s) if isinstance(s, str) else s

# %% ../nbs/11_xml.ipynb
def _to_attr(k,v):
    if isinstance(v,bool):
        if v==True : return str(k)
        if v==False: return ''
    if isinstance(v,str): v = escape(v, quote=False)
    elif isinstance(v, Mapping): v = json.dumps(v)
    else: v = str(v)
    qt = '"'
    if qt in v:
        qt = "'"
        if "'" in v: v = v.replace("'", "&#39;")
    return f'{k}={qt}{v}{qt}'

# %% ../nbs/11_xml.ipynb
def _to_xml(elm, lvl, indent:bool):
    nl = '\n'
    if not indent: lvl,nl = 0,''
    if elm is None: return ''
    if hasattr(elm, '__ft__'): elm = elm.__ft__()
    if isinstance(elm, tuple): return f'{nl}'.join(to_xml(o, indent=indent) for o in elm)
    if isinstance(elm, bytes): return elm.decode('utf-8')
    sp = ' ' * lvl
    if not isinstance(elm, FT): return f'{_escape(elm)}{nl}'

    tag,cs,attrs = elm.list
    stag = tag
    if attrs:
        sattrs = (_to_attr(k,v) for k,v in attrs.items())
        stag += ' ' + ' '.join(sattrs)

    isvoid = getattr(elm, 'void_', False)
    cltag = '' if isvoid else f'</{tag}>'
    if not cs: return f'{sp}<{stag}>{cltag}{nl}'
    if len(cs)==1 and not isinstance(cs[0],(list,tuple)) and not hasattr(cs[0],'__ft__'):
        return f'{sp}<{stag}>{_escape(cs[0])}{cltag}{nl}'
    res = f'{sp}<{stag}>{nl}'
    res += ''.join(to_xml(c, lvl=lvl+2, indent=indent) for c in cs)
    if not isvoid: res += f'{sp}{cltag}{nl}'
    return Safe(res)

def to_xml(elm, lvl=0, indent:bool=True):
    "Convert `ft` element tree into an XML string"
    return Safe(_to_xml(elm, lvl, indent))

FT.__html__ = to_xml

# %% ../nbs/11_xml.ipynb
def highlight(s, lang='html'):
    "Markdown to syntax-highlight `s` in language `lang`"
    return f'```{lang}\n{to_xml(s)}\n```'

# %% ../nbs/11_xml.ipynb
def showtags(s):
    return f"""<code><pre>
{escape(to_xml(s))}
</code></pre>"""

FT._repr_markdown_ = highlight

# %% ../nbs/11_xml.ipynb
def __getattr__(tag):
    if tag.startswith('_') or tag[0].islower(): raise AttributeError
    def _f(*c, target_id=None, **kwargs): return ft(tag, *c, target_id=target_id, **kwargs)
    return _f

# %% ../nbs/11_xml.ipynb
@patch
def __call__(self:FT, *c, **kw):
    c,kw = _preproc(c,kw)
    if c: self = self+c
    if kw: self.attrs = {**self.attrs, **kw}
    return self
