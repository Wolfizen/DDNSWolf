import importlib
import pkgutil
from types import ModuleType
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


def import_all_submodules(parent_module: Union[str, ModuleType]) -> None:
    """
    Recursively imports all submodules of the given module. Ensures that all classes are loaded, and all import-time code is
    executed. Required by find_all_subclasses() to get accurate results.
    https://stackoverflow.com/a/25562415
    """
    if isinstance(parent_module, str):
        parent_module = importlib.import_module(parent_module)
    for loader, name, is_pkg in pkgutil.walk_packages(parent_module.__path__):
        full_name = parent_module.__name__ + '.' + name
        importlib.import_module(full_name)
        if is_pkg:
            import_all_submodules(full_name)


C = TypeVar('C')


def find_all_subclasses(parent_cls: Type[C]) -> Iterable[Type[C]]:
    """
    Recursively iterates through all subclasses of the given class. You should call import_all_submodules() before this
    to ensure that all of the classes are actually loaded.
    https://stackoverflow.com/a/33607093
    """
    for cls in parent_cls.__subclasses__():
        yield from find_all_subclasses(cls)
        yield cls
