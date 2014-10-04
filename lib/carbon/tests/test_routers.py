import unittest
if not hasattr(unittest.TestCase, 'assertIsNotNone'):
    import unittest2 as unittest

from ConfigParser import RawConfigParser

from carbon.routers import RelayRulesRouter, ConsistentHashingRouter, AggregatedConsistentHashingRouter


class RelayRulesRouterTest(unittest.TestCase):

    def setUp(self):
        self.rules_config = RawConfigParser()
        self.rules_config.add_section("base")
        self.rules_config.set("base", "default", "true")
        self.rules_config.set("base", "destinations", "127.0.0.1:2004:a, 127.0.0.1:2004:b")

    def write_rules_config(self, name="relay-rules.conf"):
        with open(name, 'wb') as cfgfile:
            self.rules_config.write(cfgfile)
        return name

    def test_add_destination(self):
        rules_config = self.write_rules_config()
        router = RelayRulesRouter(rules_config)
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([]), destinations)
        router.addDestination(("127.0.0.1", 2004, "a"))
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([('127.0.0.1', 2004, 'a')]),
                         destinations)
        router.addDestination(("127.0.0.1", 2004, "b"))
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([('127.0.0.1', 2004, 'a'), ('127.0.0.1', 2004, 'b')]),
                         destinations)

    def test_remove_destination(self):
        rules_config = self.write_rules_config()
        router = RelayRulesRouter(rules_config)
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([]), destinations)
        router.addDestination(("127.0.0.1", 2004, "a"))
        router.addDestination(("127.0.0.1", 2004, "b"))
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([('127.0.0.1', 2004, 'a'), ('127.0.0.1', 2004, 'b')]),
                         destinations)
        router.removeDestination(("127.0.0.1", 2004, "b"))
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([('127.0.0.1', 2004, 'a')]),
                         destinations)

    def test_simple_regex_rules(self):
        self.rules_config.add_section("next")
        self.rules_config.set("next", "pattern", "^foo")
        self.rules_config.set("next", "destinations", "127.0.0.1:2004:b")
        rules_config = self.write_rules_config()
        router = RelayRulesRouter(rules_config)
        router.addDestination(("127.0.0.1", 2004, "a"))
        router.addDestination(("127.0.0.1", 2004, "b"))
        destinations = set(router.getDestinations("foo.a.b.c"))
        self.assertEqual(set([('127.0.0.1', 2004, 'b')]),
                         destinations)


class ConsistentHashingRouterTest(unittest.TestCase):

    def test_simple_hash_rung(self):
        router = ConsistentHashingRouter()
        router.addDestination(("127.0.0.1", 2004, "a"))
        router.addDestination(("127.0.0.1", 2004, "b"))
        destinations = set(router.getDestinations("a.b.c"))
        self.assertEqual(set([('127.0.0.1', 2004, 'a')]),
                         destinations)
        destinations = set(router.getDestinations("c.b.a"))
        self.assertEqual(set([('127.0.0.1', 2004, 'b')]),
                         destinations)
