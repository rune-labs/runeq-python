import inspect
from types import ModuleType
from typing import Callable
from unittest import TestCase

from runeq import Config, resources
from runeq.resources.session.session import Session

SKIP_MODULES = ["client", "common"]


class TestConfig(TestCase):
    def test_coverage(self):
        session = Session(Config())

        for module_name, module in inspect.getmembers(resources):
            if self.valid_module(module_name, module):
                for method_name, method in inspect.getmembers(module):
                    if self.valid_method(
                        method_name, method
                    ) and self.method_defined_in_module(method, module):
                        self.assertTrue(
                            hasattr(session, module_name),
                            f"Resource {module_name} not found in session",
                        )

                        namespace = getattr(session, module_name)
                        self.assertTrue(
                            hasattr(namespace, method_name),
                            f"Method {method_name} not found in session",
                        )

    def valid_module(self, module_name: str, module: ModuleType) -> bool:
        return (
            inspect.ismodule(module)
            and not module_name.startswith("_")
            and module_name not in SKIP_MODULES
        )

    def valid_method(self, method_name: str, method: Callable) -> bool:
        return inspect.isfunction(method) and not method_name.startswith("_")

    def method_defined_in_module(self, method: Callable, module: ModuleType) -> bool:
        return inspect.getmodule(method) == module
