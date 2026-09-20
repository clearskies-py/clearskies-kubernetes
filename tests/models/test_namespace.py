import unittest

import clearskies

import clearskies_kubernetes


class TestNamespace(unittest.TestCase):
    def test_valid(self):
        # There's no actual logic in the models so we just test that they are buildable.
        di = clearskies.di.Di(modules=[clearskies_kubernetes])
        namespaces = di.build_class(clearskies_kubernetes.models.Namespace)
