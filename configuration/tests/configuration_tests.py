# -*- coding: utf-8 -*-
import unittest
import json
from argparse import Namespace

from configuration.config import Config, num_to_chars, generate_state_labels
from configuration.parser import parser
from electoral_sys.seat_assignment import seat_assignment_rules
from simulation.base import majority_propagation
from net_generation.base import consensus_initial_state


class DummyParser(Namespace):

    def __init__(self, **kwargs):
        self.alternative_systems = None
        self.avg_deg = 12.0
        self.config_file = None
        self.consensus = False
        self.district_coords = None
        self.district_sizes = None
        self.epsilon = 0.01
        self.euclidean = False
        self.mass_media = None
        self.mc_steps = 50
        self.n = 1875
        self.n_zealots = 1
        self.num_parties = 2
        self.planar_c = None
        self.propagation = 'standard'
        self.q = 25
        self.random_dist = False
        self.ratio = 0.02
        self.reset = False
        self.sample_size = 500
        self.seat_rule = 'simple'
        self.seats = [1]
        self.therm_time = 300000
        self.threshold = 0.0
        self.where_zealots = 'random'
        self.zealots_district = None
        self.short_suffix = False
        super().__init__(**kwargs)


class SillyAttribute:

    def __getattribute__(self, item):
        return "something that definitely is not a 'dest' name of any parameter in the argument parser"


class ArgumentDict(dict):
    """
    A class to pass as the 2nd argument for Config instead of parser._option_string_actions,
    after getting an item and then an attribute, like arg_dict[argument].dest, it should return something
    that is not present in the configuration file, not to raise an error.
    """
    def __getitem__(self, key):
        return SillyAttribute()


class MockConfigFile:

    def __init__(self, **kwargs):
        self.name = 'mock config file'
        self.config_file = dict({
            'avg_deg': 5,
            'num_parties': 4,
            'propagation': 'majority',
            'seat_rule': 'hare',
            'therm_time': 15654,
        }, **kwargs)

    def read(self):
        return json.dumps(self.config_file)


class TestConfiguration(unittest.TestCase):

    def assertHasAttr(self, obj, intended_attr):
        """
        Helper function to assert if the object 'obj' has the attribute 'intended_attr' with a nice message.
        """
        test_bool = hasattr(obj, intended_attr)
        self.assertTrue(test_bool, msg=f"'{obj}' is lacking an attribute '{intended_attr}'")

    def test_num_to_chars(self):
        res = num_to_chars(27)
        self.assertEqual(res, 'ab')

    def test_num_to_chars_error1(self):
        def inner():
            num_to_chars(-10)
        self.assertRaises(ValueError, inner)

    def test_num_to_chars_error2(self):
        def inner():
            num_to_chars(10.0)
        self.assertRaises(ValueError, inner)

    def test_generate_state_labels(self):
        res = generate_state_labels(53)
        self.assertListEqual(res,
                             ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                              's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah',
                              'ai', 'aj', 'ak', 'al', 'am', 'an', 'ao', 'ap', 'aq', 'ar', 'as', 'at', 'au', 'av', 'aw',
                              'ax', 'ay', 'az', 'ba'])

    def test_config_basic_class_attributes(self):
        # might be silly to test whether some attributes exist, but it might help to think through future changes
        # and all the parser actions should be defined as class attributes of Config, so instances know they have them
        self.maxDiff = None
        self.assertIn('countrywide_system', Config.voting_systems.keys())
        self.assertIn('main_district_system', Config.voting_systems.keys())
        for action in parser._actions:
            if action.dest != 'help':
                self.assertHasAttr(Config, action.dest)

        self.assertHasAttr(Config, 'zealot_state')
        self.assertHasAttr(Config, 'not_zealot_state')
        self.assertHasAttr(Config, 'all_states')

        self.assertTrue(callable(Config.initialize_states))
        self.assertTrue(callable(Config.propagate))
        self.assertTrue(callable(Config.mutate))

    def test_config_basic_attributes_values(self):
        self.maxDiff = None
        config = Config(DummyParser(), ArgumentDict())

        test_parser = DummyParser(district_sizes=[75 for _ in range(25)], mass_media=0.5)

        for action in parser._actions:
            if action.dest != 'help':
                self.assertEqual(config.__getattribute__(action.dest), test_parser.__getattribute__(action.dest),
                                 msg=f'Attribute {action.dest} different than expected')

        self.assertEqual(config.zealot_state, 'a')
        self.assertEqual(config.not_zealot_state, 'b')
        self.assertEqual(config.all_states, ['a', 'b'])

        self.assertTrue(callable(config.initialize_states))
        self.assertTrue(callable(config.propagate))
        self.assertTrue(callable(config.mutate))

    def test_config_attributes_values_alternative_sys(self):
        self.maxDiff = None
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'basic', 'seat_rule': 'hare', 'threshold': 0.2, 'seats': [2]},
            {'name': 'two', 'type': 'merge', 'dist_merging': [1], 'threshold': 0.3},
            {'name': 'three', 'type': 'merge', 'seat_rule': 'droop', 'dist_merging': [1] * 20 + [2] * 5, 'seats': [3]},
        ]
        config = Config(input_parser, ArgumentDict())

        self.assertListEqual(list(config.voting_systems.keys()),
                             ['countrywide_system', 'main_district_system', 'one', 'two', 'three'])
        self.assertDictEqual(config.alternative_systems[0],
                             {'name': 'one', 'type': 'basic', 'seat_rule': 'hare', 'threshold': 0.2,
                              'seat_alloc_function': seat_assignment_rules['hare'], 'seats': [2],
                              'seats_per_district': [2] * 25, 'total_seats': 50})
        self.assertDictEqual(config.alternative_systems[1],
                             {'name': 'two', 'type': 'merge', 'seat_rule': config.seat_rule,
                              'seat_alloc_function': config.seat_alloc_function, 'threshold': 0.3, 'q': 1,
                              'total_seats': config.total_seats, 'seats': None, 'dist_merging': [1]})
        self.assertDictEqual(config.alternative_systems[2],
                             {'name': 'three', 'type': 'merge', 'seat_rule': 'droop',
                              'seat_alloc_function': seat_assignment_rules['droop'], 'threshold': config.threshold,
                              'q': 2, 'total_seats': 75, 'dist_merging': [1] * 20 + [2] * 5, 'seats': [3],
                              'seats_per_district': [3] * 25})

    def test_config_attributes_values_alternative_sys_error_no_name(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'type': 'basic', 'seat_rule': 'hare', 'threshold': 0.2},
        ]
        self.assertRaises(KeyError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_no_type(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'seat_rule': 'hare'},
        ]
        self.assertRaises(KeyError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_name_duplicate(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'basic', 'seat_rule': 'hare', 'threshold': 0.2},
            {'name': 'one', 'type': 'basic', 'seat_rule': 'hare', 'threshold': 0.2},
        ]
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_threshold(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'basic', 'seat_rule': 'hare', 'threshold': -0.2},
        ]
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_seat_rule(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'basic', 'seat_rule': 'wrong_seat_rule'},
        ]
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_seats(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'basic', 'seats': []},
        ]
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_no_dist_merging(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'merge'},
        ]
        self.assertRaises(KeyError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_wrong_dist_merging(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'merge', 'dist_merging': 1},
        ]
        self.assertRaises(KeyError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_wrong_dist_merging2(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'merge', 'dist_merging': []},
        ]
        self.assertRaises(KeyError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_alternative_sys_error_too_short_dist_merging(self):
        input_parser = DummyParser()
        input_parser.alternative_systems = [
            {'name': 'one', 'type': 'merge', 'dist_merging': [1, 2, 3]},
        ]
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_basic_attributes_values_config_file(self):
        input_parser = DummyParser()
        input_parser.config_file = MockConfigFile()
        config = Config(input_parser, ArgumentDict())
        self.assertEqual(config.config_file, 'mock config file')
        self.assertEqual(config.avg_deg, 5)
        self.assertEqual(config.num_parties, 4)
        self.assertEqual(config.propagation, 'majority')
        self.assertEqual(config.propagate, majority_propagation)
        self.assertEqual(config.seat_rule, 'hare')
        self.assertEqual(config.therm_time, 15654)

    def test_config_basic_attributes_values_config_file_threshold_error(self):
        input_parser = DummyParser()
        input_parser.config_file = MockConfigFile(threshold=1.1)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_threshold_too_low(self):
        input_parser = DummyParser(threshold=-1)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_threshold_too_high(self):
        input_parser = DummyParser(threshold=1.5)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_district_sizes_too_few(self):
        input_parser = DummyParser(district_sizes=[1800, 75])
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_district_sizes_too_many(self):
        input_parser = DummyParser(district_sizes=[25]*75)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_district_sizes_wrong_sum(self):
        input_parser = DummyParser(district_sizes=[10]*25)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_n_q_wrong(self):
        input_parser = DummyParser(n=1876)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_district_coords_too_few(self):
        input_parser = DummyParser(district_coords=[[1, 2], [3, 4]])
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_district_coords_too_many(self):
        input_parser = DummyParser(district_coords=[[1, 2]]*26)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_parties_too_few(self):
        input_parser = DummyParser(num_parties=1)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_consensus(self):
        input_parser = DummyParser(consensus=True)
        config = Config(input_parser, ArgumentDict())
        self.assertEqual(config.initialize_states, consensus_initial_state)

    def test_config_attributes_values_zealots_degree(self):
        input_parser = DummyParser(where_zealots='degree', zealots_district=223)
        config = Config(input_parser, ArgumentDict())
        self.assertDictEqual(config.zealots_config, {'degree_driven': True, 'one_district': False, 'district': None})

    def test_config_attributes_values_zealots_dist(self):
        input_parser = DummyParser(where_zealots='district', zealots_district=12)
        config = Config(input_parser, ArgumentDict())
        self.assertDictEqual(config.zealots_config, {'degree_driven': False, 'one_district': True, 'district': 12})

    def test_config_attributes_values_zealots_random(self):
        input_parser = DummyParser(where_zealots='random')
        config = Config(input_parser, ArgumentDict())
        self.assertDictEqual(config.zealots_config, {'degree_driven': False, 'one_district': False, 'district': None})

    def test_config_attributes_values_mass_media_too_low(self):
        input_parser = DummyParser(mass_media=-0.1)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_mass_media_too_high(self):
        input_parser = DummyParser(mass_media=1.1)
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_seats_empty(self):
        input_parser = DummyParser(seats=[])
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())

    def test_config_attributes_values_wrong_seat_rule(self):
        input_parser = DummyParser(seat_rule='wrong seat rule 123')
        self.assertRaises(ValueError, Config, input_parser, ArgumentDict())


if __name__ == '__main__':
    unittest.main()
