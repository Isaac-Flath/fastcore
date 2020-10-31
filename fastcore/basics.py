# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_basics.ipynb (unless otherwise specified).

__all__ = ['defaults', 'ifnone', 'maybe_attr', 'basic_repr', 'is_array', 'listify', 'true', 'NullType', 'null',
           'tonull', 'get_class', 'mk_class', 'wrap_class', 'ignore_exceptions', 'exec_local', 'risinstance', 'Inf',
           'in_', 'lt', 'gt', 'le', 'ge', 'eq', 'ne', 'add', 'sub', 'mul', 'truediv', 'is_', 'is_not', 'in_', 'true',
           'stop', 'gen', 'chunked', 'otherwise', 'custom_dir', 'AttrDict', 'with_cast', 'store_attr', 'attrdict',
           'properties', 'camel2snake', 'snake2camel', 'class2attr', 'hasattrs', 'setattrs', 'try_attrs', 'ShowPrint',
           'Int', 'Str', 'Float', 'detuplify', 'replicate', 'setify', 'merge', 'range_of', 'groupby', 'last_index',
           'filter_dict', 'filter_keys', 'filter_values', 'cycle', 'zip_cycle', 'sorted_ex', 'negate_func', 'argwhere',
           'filter_ex', 'range_of', 'renumerate', 'first', 'nested_attr', 'nested_idx', 'num_methods', 'rnum_methods',
           'inum_methods', 'fastuple', 'arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'bind', 'map_ex', 'compose', 'maps',
           'partialler', 'instantiate', 'using_attr', 'Self', 'Self', 'PrettyString', 'even_mults', 'num_cpus',
           'add_props', 'typed']

# Cell
from .imports import *

# Cell
defaults = SimpleNamespace()

# Cell
def ifnone(a, b):
    "`b` if `a` is None else `a`"
    return b if a is None else a

# Cell
def maybe_attr(o, attr):
    "`getattr(o,attr,o)`"
    return getattr(o,attr,o)

# Cell
def basic_repr(flds=None):
    if isinstance(flds, str): flds = re.split(', *', flds)
    flds = list(flds or [])
    def _f(self):
        sig = ', '.join(f'{o}={maybe_attr(getattr(self,o), "__name__")}' for o in flds)
        return f'{self.__class__.__name__}({sig})'
    return _f

# Cell
def is_array(x):
    "`True` if `x` supports `__array__` or `iloc`"
    return hasattr(x,'__array__') or hasattr(x,'iloc')

# Cell
def listify(o):
    "Convert `o` to a `list`"
    if o is None: return []
    if isinstance(o, list): return o
    if isinstance(o, str) or is_array(o): return [o]
    if is_iter(o): return list(o)
    return [o]

# Cell
def true(x):
    "Test whether `x` is truthy; collections with >0 elements are considered `True`"
    try: return bool(len(x))
    except: return bool(x)

# Cell
class NullType:
    "An object that is `False` and can be called, chained, and indexed"
    def __getattr__(self,*args):return null
    def __call__(self,*args, **kwargs):return null
    def __getitem__(self, *args):return null
    def __bool__(self): return False

null = NullType()

# Cell
def tonull(x):
    "Convert `None` to `null`"
    return null if x is None else x

# Cell
def get_class(nm, *fld_names, sup=None, doc=None, funcs=None, **flds):
    "Dynamically create a class, optionally inheriting from `sup`, containing `fld_names`"
    attrs = {}
    for f in fld_names: attrs[f] = None
    for f in listify(funcs): attrs[f.__name__] = f
    for k,v in flds.items(): attrs[k] = v
    sup = ifnone(sup, ())
    if not isinstance(sup, tuple): sup=(sup,)

    def _init(self, *args, **kwargs):
        for i,v in enumerate(args): setattr(self, list(attrs.keys())[i], v)
        for k,v in kwargs.items(): setattr(self,k,v)

    all_flds = [*fld_names,*flds.keys()]
    def _eq(self,b):
        return all([getattr(self,k)==getattr(b,k) for k in all_flds])

    if not sup: attrs['__repr__'] = basic_repr(all_flds)
    attrs['__init__'] = _init
    attrs['__eq__'] = _eq
    res = type(nm, sup, attrs)
    if doc is not None: res.__doc__ = doc
    return res

# Cell
def mk_class(nm, *fld_names, sup=None, doc=None, funcs=None, mod=None, **flds):
    "Create a class using `get_class` and add to the caller's module"
    if mod is None: mod = sys._getframe(1).f_locals
    res = get_class(nm, *fld_names, sup=sup, doc=doc, funcs=funcs, **flds)
    mod[nm] = res

# Cell
def wrap_class(nm, *fld_names, sup=None, doc=None, funcs=None, **flds):
    "Decorator: makes function a method of a new class `nm` passing parameters to `mk_class`"
    def _inner(f):
        mk_class(nm, *fld_names, sup=sup, doc=doc, funcs=listify(funcs)+[f], mod=f.__globals__, **flds)
        return f
    return _inner

# Cell
class ignore_exceptions:
    "Context manager to ignore exceptions"
    def __enter__(self): pass
    def __exit__(self, *args): return True

# Cell
def exec_local(code, var_name):
    "Call `exec` on `code` and return the var `var_name"
    loc = {}
    exec(code, globals(), loc)
    return loc[var_name]

# Cell
def risinstance(types, obj=None):
    "Curried `isinstance` but with args reversed"
    if not obj: return partial(risinstance,types)
    return isinstance(obj, types)

# Cell
#hide
class _InfMeta(type):
    @property
    def count(self): return itertools.count()
    @property
    def zeros(self): return itertools.cycle([0])
    @property
    def ones(self):  return itertools.cycle([1])
    @property
    def nones(self): return itertools.cycle([None])

# Cell
class Inf(metaclass=_InfMeta):
    "Infinite lists"
    pass

# Cell
_dumobj = object()
def _oper(op,a,b=_dumobj): return (lambda o:op(o,a)) if b is _dumobj else op(a,b)

def _mk_op(nm, mod):
    "Create an operator using `oper` and add to the caller's module"
    op = getattr(operator,nm)
    def _inner(a, b=_dumobj): return _oper(op, a,b)
    _inner.__name__ = _inner.__qualname__ = nm
    _inner.__doc__ = f'Same as `operator.{nm}`, or returns partial if 1 arg'
    mod[nm] = _inner

# Cell
def in_(x, a):
    "`True` if `x in a`"
    return x in a

operator.in_ = in_

# Cell
#nbdev_comment _all_ = ['lt','gt','le','ge','eq','ne','add','sub','mul','truediv','is_','is_not','in_']

# Cell
for op in ['lt','gt','le','ge','eq','ne','add','sub','mul','truediv','is_','is_not','in_']: _mk_op(op, globals())

# Cell
def true(*args, **kwargs):
    "Predicate: always `True`"
    return True

# Cell
def stop(e=StopIteration):
    "Raises exception `e` (by default `StopException`)"
    raise e

# Cell
def gen(func, seq, cond=true):
    "Like `(func(o) for o in seq if cond(func(o)))` but handles `StopIteration`"
    return itertools.takewhile(cond, map(func,seq))

# Cell
def chunked(it, chunk_sz=None, drop_last=False, n_chunks=None):
    "Return batches from iterator `it` of size `chunk_sz` (or return `n_chunks` total)"
    assert bool(chunk_sz) ^ bool(n_chunks)
    if n_chunks: chunk_sz = math.ceil(len(it)/n_chunks)
    if not isinstance(it, Iterator): it = iter(it)
    while True:
        res = list(itertools.islice(it, chunk_sz))
        if res and (len(res)==chunk_sz or not drop_last): yield res
        if len(res)<chunk_sz: return

# Cell
def otherwise(x, tst, y):
    "`y if tst(x) else x`"
    return y if tst(x) else x

# Cell
def custom_dir(c, add:list):
    "Implement custom `__dir__`, adding `add` to `cls`"
    return dir(type(c)) + list(c.__dict__.keys()) + add

# Cell
class AttrDict(dict):
    "`dict` subclass that also provides access to keys as attrs"
    def __getattr__(self,k): return self[k] if k in self else stop(AttributeError(k))
    def __setattr__(self, k, v): (self.__setitem__,super().__setattr__)[k[0]=='_'](k,v)
    def __dir__(self): return custom_dir(self, list(self.keys()))

# Cell
def with_cast(f):
    "Decorator which uses any parameter annotations as preprocessing functions"
    anno = f.__annotations__
    params = f.__code__.co_varnames[:f.__code__.co_argcount]
    defaults = dict(zip(reversed(params), reversed(f.__defaults__))) if f.__defaults__ else {}
    @functools.wraps(f)
    def _inner(*args, **kwargs):
        args = list(args)
        for i,v in enumerate(params):
            if v in anno:
                c = anno[v]
                if v in kwargs: kwargs[v] = c(kwargs[v])
                elif i<len(args): args[i] = c(args[i])
                elif v in defaults: kwargs[v] = c(defaults[v])
        return f(*args, **kwargs)
    return _inner

# Cell
def _store_attr(self, anno, **attrs):
    for n,v in attrs.items():
        if n in anno: v = anno[n](v)
        setattr(self, n, v)
        self.__stored_args__[n] = v

# Cell
def store_attr(names=None, self=None, but=None, cast=False, **attrs):
    "Store params named in comma-separated `names` from calling context into attrs in `self`"
    fr = sys._getframe(1)
    args = fr.f_code.co_varnames[:fr.f_code.co_argcount]
    if self: args = ('self', *args)
    else: self = fr.f_locals[args[0]]
    if not hasattr(self, '__stored_args__'): self.__stored_args__ = {}
    anno = self.__class__.__init__.__annotations__ if cast else {}
    if attrs: return _store_attr(self, anno, **attrs)
    ns = re.split(', *', names) if names else args[1:]
    _store_attr(self, anno, **{n:fr.f_locals[n] for n in ns if n not in listify(but)})

# Cell
def attrdict(o, *ks):
    "Dict from each `k` in `ks` to `getattr(o,k)`"
    return {k:getattr(o,k) for k in ks}

# Cell
def properties(cls, *ps):
    "Change attrs in `cls` with names in `ps` to properties"
    for p in ps: setattr(cls,p,property(getattr(cls,p)))

# Cell
_camel_re1 = re.compile('(.)([A-Z][a-z]+)')
_camel_re2 = re.compile('([a-z0-9])([A-Z])')

# Cell
def camel2snake(name):
    "Convert CamelCase to snake_case"
    s1   = re.sub(_camel_re1, r'\1_\2', name)
    return re.sub(_camel_re2, r'\1_\2', s1).lower()

# Cell
def snake2camel(s):
    "Convert snake_case to CamelCase"
    return ''.join(s.title().split('_'))

# Cell
def class2attr(self, cls_name):
    "Return the snake-cased name of the class; strip ending `cls_name` if it exists."
    return camel2snake(re.sub(rf'{cls_name}$', '', self.__class__.__name__) or cls_name.lower())

# Cell
def hasattrs(o,attrs):
    "Test whether `o` contains all `attrs`"
    return all(hasattr(o,attr) for attr in attrs)

# Cell
def setattrs(dest, flds, src):
    f = dict.get if isinstance(src, dict) else getattr
    flds = re.split(r",\s*", flds)
    for fld in flds: setattr(dest, fld, f(src, fld))

# Cell
def try_attrs(obj, *attrs):
    "Return first attr that exists in `obj`"
    for att in attrs:
        try: return getattr(obj, att)
        except: pass
    raise AttributeError(attrs)

# Cell
#hide
class ShowPrint:
    "Base class that prints for `show`"
    def show(self, *args, **kwargs): print(str(self))

# Cell
#hide
class Int(int,ShowPrint):
    "An extensible `int`"
    pass

# Cell
#hide
class Str(str,ShowPrint):
    "An extensible `str`"
    pass
class Float(float,ShowPrint):
    "An extensible `float`"
    pass

# Cell
def detuplify(x):
    "If `x` is a tuple with one thing, extract it"
    return None if len(x)==0 else x[0] if len(x)==1 and getattr(x, 'ndim', 1)==1 else x

# Cell
def replicate(item,match):
    "Create tuple of `item` copied `len(match)` times"
    return (item,)*len(match)

# Cell
def setify(o):
    "Turn any list like-object into a set."
    return o if isinstance(o,set) else set(listify(o))

# Cell
def merge(*ds):
    "Merge all dictionaries in `ds`"
    return {k:v for d in ds if d is not None for k,v in d.items()}

# Cell
def range_of(x):
    "All indices of collection `x` (i.e. `list(range(len(x)))`)"
    return list(range(len(x)))

# Cell
def groupby(x, key, val=noop):
    "Like `itertools.groupby` but doesn't need to be sorted, and isn't lazy, plus some extensions"
    if   isinstance(key,int): key = itemgetter(key)
    elif isinstance(key,str): key = attrgetter(key)
    if   isinstance(val,int): val = itemgetter(val)
    elif isinstance(val,str): val = attrgetter(val)
    res = {}
    for o in x: res.setdefault(key(o), []).append(val(o))
    return res

# Cell
def last_index(x, o):
    "Finds the last index of occurence of `x` in `o` (returns -1 if no occurence)"
    try: return next(i for i in reversed(range(len(o))) if o[i] == x)
    except StopIteration: return -1

# Cell
def filter_dict(d, func):
    "Filter a `dict` using `func`, applied to keys and values"
    return {k:v for k,v in d.items() if func(k,v)}

# Cell
def filter_keys(d, func):
    "Filter a `dict` using `func`, applied to keys"
    return {k:v for k,v in d.items() if func(k)}

# Cell
def filter_values(d, func):
    "Filter a `dict` using `func`, applied to values"
    return {k:v for k,v in d.items() if func(v)}

# Cell
def cycle(o):
    "Like `itertools.cycle` except creates list of `None`s if `o` is empty"
    o = listify(o)
    return itertools.cycle(o) if o is not None and len(o) > 0 else itertools.cycle([None])

# Cell
def zip_cycle(x, *args):
    "Like `itertools.zip_longest` but `cycle`s through elements of all but first argument"
    return zip(x, *map(cycle,args))

# Cell
def sorted_ex(iterable, key=None, reverse=False):
    "Like `sorted`, but if key is str use `attrgetter`; if int use `itemgetter`"
    if isinstance(key,str):   k=lambda o:getattr(o,key,0)
    elif isinstance(key,int): k=itemgetter(key)
    else: k=key
    return sorted(iterable, key=k, reverse=reverse)

# Cell
def negate_func(f):
    "Create new function that negates result of `f`"
    def _f(*args, **kwargs): return not f(*args, **kwargs)
    return _f

# Cell
def argwhere(iterable, f, negate=False, **kwargs):
    "Like `filter_ex`, but return indices for matching items"
    if kwargs: f = partial(f,**kwargs)
    if negate: f = negate_func(f)
    return [i for i,o in enumerate(iterable) if f(o)]

# Cell
def filter_ex(iterable, f=noop, negate=False, gen=False, **kwargs):
    "Like `filter`, but passing `kwargs` to `f`, defaulting `f` to `noop`, and adding `negate` and `gen`"
    if f is None: f = lambda _: True
    if kwargs: f = partial(f,**kwargs)
    if negate: f = negate_func(f)
    res = filter(f, iterable)
    if gen: return res
    return list(res)

# Cell
def range_of(a, b=None, step=None):
    "All indices of collection `a`, if `a` is a collection, otherwise `range`"
    if is_coll(a): a = len(a)
    return list(range(a,b,step) if step is not None else range(a,b) if b is not None else range(a))

# Cell
def renumerate(iterable, start=0):
    "Same as `enumerate`, but returns index as 2nd element instead of 1st"
    return ((o,i) for i,o in enumerate(iterable, start=start))

# Cell
def first(x, f=None, negate=False, **kwargs):
    "First element of `x`, or None if missing"
    x = iter(x)
    if f: x = filter_ex(x, f=f, negate=negate, gen=True, **kwargs)
    try: return next(x)
    except StopIteration: return None

# Cell
def nested_attr(o, attr, default=None):
    "Same as `getattr`, but if `attr` includes a `.`, then looks inside nested objects"
    try:
        for a in attr.split("."): o = getattr(o, a)
    except AttributeError: return default
    return o

# Cell
def nested_idx(coll, *idxs):
    "Index into nested collections, dicts, etc, with `idxs`"
    if not coll or not idxs: return coll
    if isinstance(coll,str) or not isinstance(coll, typing.Collection): return None
    res = coll.get(idxs[0], None) if hasattr(coll, 'get') else coll[idxs[0]] if idxs[0]<len(coll) else None
    return nested_idx(res, *idxs[1:])

# Cell
num_methods = """
    __add__ __sub__ __mul__ __matmul__ __truediv__ __floordiv__ __mod__ __divmod__ __pow__
    __lshift__ __rshift__ __and__ __xor__ __or__ __neg__ __pos__ __abs__
""".split()
rnum_methods = """
    __radd__ __rsub__ __rmul__ __rmatmul__ __rtruediv__ __rfloordiv__ __rmod__ __rdivmod__
    __rpow__ __rlshift__ __rrshift__ __rand__ __rxor__ __ror__
""".split()
inum_methods = """
    __iadd__ __isub__ __imul__ __imatmul__ __itruediv__
    __ifloordiv__ __imod__ __ipow__ __ilshift__ __irshift__ __iand__ __ixor__ __ior__
""".split()

# Cell
class fastuple(tuple):
    "A `tuple` with elementwise ops and more friendly __init__ behavior"
    def __new__(cls, x=None, *rest):
        if x is None: x = ()
        if not isinstance(x,tuple):
            if len(rest): x = (x,)
            else:
                try: x = tuple(iter(x))
                except TypeError: x = (x,)
        return super().__new__(cls, x+rest if rest else x)

    def _op(self,op,*args):
        if not isinstance(self,fastuple): self = fastuple(self)
        return type(self)(map(op,self,*map(cycle, args)))

    def mul(self,*args):
        "`*` is already defined in `tuple` for replicating, so use `mul` instead"
        return fastuple._op(self, operator.mul,*args)

    def add(self,*args):
        "`+` is already defined in `tuple` for concat, so use `add` instead"
        return fastuple._op(self, operator.add,*args)

def _get_op(op):
    if isinstance(op,str): op = getattr(operator,op)
    def _f(self,*args): return self._op(op,*args)
    return _f

for n in num_methods:
    if not hasattr(fastuple, n) and hasattr(operator,n): setattr(fastuple,n,_get_op(n))

for n in 'eq ne lt le gt ge'.split(): setattr(fastuple,n,_get_op(n))
setattr(fastuple,'__invert__',_get_op('__not__'))
setattr(fastuple,'max',_get_op(max))
setattr(fastuple,'min',_get_op(min))

# Cell
class _Arg:
    def __init__(self,i): self.i = i
arg0 = _Arg(0)
arg1 = _Arg(1)
arg2 = _Arg(2)
arg3 = _Arg(3)
arg4 = _Arg(4)

# Cell
class bind:
    "Same as `partial`, except you can use `arg0` `arg1` etc param placeholders"
    def __init__(self, fn, *pargs, **pkwargs):
        self.fn,self.pargs,self.pkwargs = fn,pargs,pkwargs
        self.maxi = max((x.i for x in pargs if isinstance(x, _Arg)), default=-1)

    def __call__(self, *args, **kwargs):
        args = list(args)
        kwargs = {**self.pkwargs,**kwargs}
        for k,v in kwargs.items():
            if isinstance(v,_Arg): kwargs[k] = args.pop(v.i)
        fargs = [args[x.i] if isinstance(x, _Arg) else x for x in self.pargs] + args[self.maxi+1:]
        return self.fn(*fargs, **kwargs)

# Cell
def map_ex(iterable, f, *args, gen=False, **kwargs):
    "Like `map`, but use `bind`, and supports `str` and indexing"
    g = (bind(f,*args,**kwargs) if callable(f)
         else f.format if isinstance(f,str)
         else f.__getitem__)
    res = map(g, iterable)
    if gen: return res
    return list(res)

# Cell
def compose(*funcs, order=None):
    "Create a function that composes all functions in `funcs`, passing along remaining `*args` and `**kwargs` to all"
    funcs = listify(funcs)
    if len(funcs)==0: return noop
    if len(funcs)==1: return funcs[0]
    if order is not None: funcs = sorted_ex(funcs, key=order)
    def _inner(x, *args, **kwargs):
        for f in funcs: x = f(x, *args, **kwargs)
        return x
    return _inner

# Cell
def maps(*args, retain=noop):
    "Like `map`, except funcs are composed first"
    f = compose(*args[:-1])
    def _f(b): return retain(f(b), b)
    return map(_f, args[-1])

# Cell
def partialler(f, *args, order=None, **kwargs):
    "Like `functools.partial` but also copies over docstring"
    fnew = partial(f,*args,**kwargs)
    fnew.__doc__ = f.__doc__
    if order is not None: fnew.order=order
    elif hasattr(f,'order'): fnew.order=f.order
    return fnew

# Cell
def instantiate(t):
    "Instantiate `t` if it's a type, otherwise do nothing"
    return t() if isinstance(t, type) else t

# Cell
def _using_attr(f, attr, x): return f(getattr(x,attr))

# Cell
def using_attr(f, attr):
    "Change function `f` to operate on `attr`"
    return partial(_using_attr, f, attr)

# Cell
class _Self:
    "An alternative to `lambda` for calling methods on passed object."
    def __init__(self): self.nms,self.args,self.kwargs,self.ready = [],[],[],True
    def __repr__(self): return f'self: {self.nms}({self.args}, {self.kwargs})'

    def __call__(self, *args, **kwargs):
        if self.ready:
            x = args[0]
            for n,a,k in zip(self.nms,self.args,self.kwargs):
                x = getattr(x,n)
                if callable(x) and a is not None: x = x(*a, **k)
            return x
        else:
            self.args.append(args)
            self.kwargs.append(kwargs)
            self.ready = True
            return self

    def __getattr__(self,k):
        if not self.ready:
            self.args.append(None)
            self.kwargs.append(None)
        self.nms.append(k)
        self.ready = False
        return self

# Cell
class _SelfCls:
    def __getattr__(self,k): return getattr(_Self(),k)
    def __getitem__(self,i): return self.__getattr__('__getitem__')(i)

Self = _SelfCls()

# Cell
#nbdev_comment _all_ = ['Self']

# Cell
class PrettyString(str):
    "Little hack to get strings to show properly in Jupyter."
    def __repr__(self): return self

# Cell
def even_mults(start, stop, n):
    "Build log-stepped array from `start` to `stop` in `n` steps."
    if n==1: return stop
    mult = stop/start
    step = mult**(1/(n-1))
    return [start*(step**i) for i in range(n)]

# Cell
def num_cpus():
    "Get number of cpus"
    try:                   return len(os.sched_getaffinity(0))
    except AttributeError: return os.cpu_count()

defaults.cpus = num_cpus()

# Cell
def add_props(f, g=None, n=2):
    "Create properties passing each of `range(n)` to f"
    if g is None: return (property(partial(f,i)) for i in range(n))
    return (property(partial(f,i), partial(g,i)) for i in range(n))

# Cell
def _typeerr(arg, val, typ): return TypeError(f"{arg}=={val} not {typ}")

# Cell
def typed(f):
    "Decorator to check param and return types at runtime"
    names = f.__code__.co_varnames
    anno = f.__annotations__
    ret = anno.pop('return',None)
    def _f(*args,**kwargs):
        kw = {**kwargs}
        if len(anno) > 0:
            for i,arg in enumerate(args): kw[names[i]] = arg
            for k,v in kw.items():
                if not isinstance(v,anno[k]): raise _typeerr(k, v, anno[k])
        res = f(*args,**kwargs)
        if ret is not None and not isinstance(res,ret): raise _typeerr("return", res, ret)
        return res
    return functools.update_wrapper(_f, f)