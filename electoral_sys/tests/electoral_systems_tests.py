# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal

from electoral_sys.electoral_system import counts_to_result


class TestElectoralSystems(unittest.TestCase):

    def test_counts_to_result_one(self):
        counts = {'a': 30, 'b': 20, 'c': 15, 'd': 35}
        total = sum(counts.values())
        res = counts_to_result(counts, total)
        self.assertDictEqual(res,
                             {'fractions': {'a': Decimal('0.3'),
                                            'b': Decimal('0.2'),
                                            'c': Decimal('0.15'),
                                            'd': Decimal('0.35')},
                              'winner': 'd'})

    def test_counts_to_result_two(self):
        counts = {'a': 35, 'b': 15, 'c': 15, 'd': 35}
        total = sum(counts.values())
        res = counts_to_result(counts, total)
        self.assertDictEqual(res['fractions'],
                             {'a': Decimal('0.35'),
                              'b': Decimal('0.15'),
                              'c': Decimal('0.15'),
                              'd': Decimal('0.35')})
        # random winner in a draw
        self.assertIn(res['winner'], ['a', 'd'])


if __name__ == '__main__':
    unittest.main()
