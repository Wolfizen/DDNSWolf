from typing import Union, TypeVar, Type, Iterable

import dns.name
from dns.name import Name


def dns_names_equal(name1: Union[str, Name], name2: Union[str, Name]) -> bool:
    """
    Compare the equality of two domain names as defined by the DNS specification. Ignores case and root name at the end.
    Can be called with strings or a Name object.
    """
    if not isinstance(name1, Name):
        name1 = dns.name.from_text(name1)
    if not isinstance(name2, Name):
        name2 = dns.name.from_text(name2)
    return name1 == name2


C = TypeVar('C')


def find_all_subclasses(parent_cls: Type[C]) -> Iterable[Type[C]]:
    """
    Recursively iterates through all subclasses of the given class.
    """
    for cls in parent_cls.__subclasses__():
        yield from find_all_subclasses(cls)
        yield cls
