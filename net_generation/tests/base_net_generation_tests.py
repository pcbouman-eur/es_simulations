# -*- coding: utf-8 -*-
import unittest

from net_generation.base import default_initial_state


class TestNetworkGeneration(unittest.TestCase):

    def test_default_initial_state(self):
        res = default_initial_state(2000, ('a', 'b', 'c'))
        self.assertEqual(len(res), 2000)
        self.assertSetEqual(set(res), {'a', 'b', 'c'})


if __name__ == '__main__':
    unittest.main()
