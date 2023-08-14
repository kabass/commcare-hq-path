import json
import sys


def print_formatted(obj, namespace={}, dict_sort_key=None, stream=sys.stdout,
                    indent=4, separators=(',', ': ')):
    """Pretty-print an object. Like `json.dump()`, but output valid
    Python code rather than JSON. Designed for Elasticsearch mappings, but usage
    is not strictly confined to only those objects.

    :param obj: object to be 'printed'
    :param namespace: (optional dict) see SortingPythonEncoder `namespace` arg
    :param dict_sort_key: (optional) see SortingPythonEncoder `dict_sort_key`
    :param stream: (optional) file-like object where output is written,
                   default=`sys.stdout`
    :param indent: (int) see `json.dump`
    :param separators: (tuple) see `json.dump`
    """
    encoder = SortingPythonEncoder(
        namespace,
        dict_sort_key=dict_sort_key,
        indent=indent,
        separators=separators,
    )
    for chunk in encoder.iterencode(obj):
        stream.write(chunk)


class SortingPythonEncoder(json.JSONEncoder):
    """Encodes an nested python dict (or otherwise JSON-serializable objects) as
    properly indented python code.

    A JSONEncoder which writes 'True', 'False' and 'None' instead of 'true',
    'false' and 'null'; with the extra ability to replace objects (provided via
    the `namespace` argument) with a literal name rather than their value
    representation."""

    # Use tuple value because hash(True)==1 and hash(False)==0
    SCALARS = {s: (s, str(s)) for s in [True, False, None]}

    def __init__(self, namespace={}, scalars=SCALARS, dict_sort_key=None, **kw):
        """
        :param namespace: (optional dict) replace output with literal name
                          (dict key) anywhere value (dict value) is found within
                          `obj`.
        :param scalars: (optional dict) collection of scalars to be replaced
                        with their python literal value. Format:
                        {<scalar>: (<scalar>, <literal_string>), ...}.
        :param dict_sort_key: (optional) dict sorting key function.
        :param **kw: additional keyword arguments are passed to `JSONEncoder`
                     verbatim.
        """
        self.scalars = scalars
        self.dict_sort_key = dict_sort_key
        self.by_name = {}
        self.by_value = {}
        for name, value in namespace.items():
            try:
                # object is hashable, store by value (faster lookup)
                self.by_value[value] = name
            except TypeError:
                # object is not hashable, store by name (slower lookup)
                self.by_name[name] = value
        super().__init__(**kw)

    def default(self, obj):
        if isinstance(obj, PythonLiteralProxy):
            if obj.registry_key is None:
                raise ValueError(f"proxy is not registered: {obj}")
            return obj.registry_key
        super().default(obj)

    def iterencode(self, o, *args, **kw):
        registry = ProxyRegistry()
        obj = self.inject_proxies(o, registry)
        for chunk in super().iterencode(obj, *args, **kw):
            yield registry.extract(chunk)
        registry.verify()

    def inject_proxies(self, obj, reg):
        try:
            scalar, name = self.scalars.get(obj, (None, None))
            if name is None or scalar is not obj:
                name = self.by_value.get(obj)
        except TypeError:
            name = None
            for key, value in self.by_name.items():
                if obj == value:
                    name = key
                    break
        if name is not None:
            return reg.make_proxy(name)
        if isinstance(obj, (tuple, list)):
            return [self.inject_proxies(v, reg) for v in obj]
        elif isinstance(obj, dict):
            injected = {}
            for key, value in sorted(obj.items(), key=self.dict_sort_key):
                injected[key] = self.inject_proxies(value, reg)
            return injected
        else:
            return obj


class ProxyRegistry:
    """Registry for managing proxy objects, allowing them to traverse the JSON
    serialization process and get printed as a name in the output."""

    PROXY_ID_DELIMITER = "__PROXY_ID_DELIMITER__"

    def __init__(self):
        self.registry = []
        self.extracted = {}

    def verify(self):
        """Ensure all registered proxies have been claimed."""
        unclaimed = [it for it in self.registry if it is not None]
        if unclaimed:
            raise ValueError(f"Unclaimed proxies: {unclaimed}")

    def make_proxy(self, name):
        """Create and return a new proxy object which can be identified and
        replaced with its name later via `extract()`."""
        index = len(self.registry)
        proxy = PythonLiteralProxy(name)
        ident = id(proxy)
        proxy.registry_key = f"{index}:{ident}{self.PROXY_ID_DELIMITER}{name}"
        self.registry.append(proxy)
        return proxy

    def extract(self, chunk):
        """Process a chunk of an object and detect if it is a proxy. If so,
        return its name (`proxy.value`) otherwise return the chunk verbatim."""
        if not chunk.startswith('"') or not chunk.endswith('"'):
            return chunk
        head, delim, tail = chunk[1:-1].partition(self.PROXY_ID_DELIMITER)
        if not delim:
            return chunk
        try:
            index, ident = [int(v) for v in head.split(":")]
            proxy = self.registry[index]
        except (ValueError, IndexError):
            return chunk
        if proxy is None and self.extracted[index] == ident:
            # FIXME: This is most likely a bug, but _could_ in fact be a valid
            # piece of data, which just "happened" to match the internal state
            # of the this registry (extremely unlucky and unlikely, highly
            # suspicious, but technically possible).
            raise ValueError(f"Invalid (already claimed) registry key: {chunk}")
        elif proxy is None or ident != id(proxy):
            # Nearly-valid registry string that has the wrong object id. This
            # actually happening in the wild would be worrying since the goal of
            # the registry key is to be sufficiently obscure to not look like
            # real data.
            return chunk
        self.extracted[index] = ident
        self.registry[index] = None
        return proxy.value


class PythonLiteralProxy:

    def __init__(self, value):
        self.value = value
        self.registry_key = None
