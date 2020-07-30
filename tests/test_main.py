import unittest
import main

class TestMain(unittest.TestCase):

    def test_get_current_layer_in_non_layer_line(self):
        layer_at = main.get_current_layer(';Layer height: 0.2')
        self.assertEqual(layer_at, None, "Parsed layer position should be None")

    def test_get_current_layer_in_non_layer_line_again(self):
        layer_at = main.get_current_layer(';LAYER_COUNT:115')
        self.assertEqual(layer_at, None, "Parsed layer position should be None")

    def test_get_current_layer(self):
        layer_at = main.get_current_layer(';LAYER:115')
        self.assertEqual(layer_at, 115, "Parsed layer position should be a number")

    def test_not_initial_layer(self):
        self.assertTrue(main.not_initial_layer(1))
        self.assertTrue(main.not_initial_layer(2))
        self.assertTrue(main.not_initial_layer(3))
        self.assertFalse(main.not_initial_layer(0))

    def test_have_to_change_variable_at_layer(self):
        self.assertFalse(main.have_to_change_variable_at_layer(1, 5))
        self.assertFalse(main.have_to_change_variable_at_layer(2, 5))
        self.assertFalse(main.have_to_change_variable_at_layer(3, 5))
        self.assertFalse(main.have_to_change_variable_at_layer(4, 5))
        self.assertTrue(main.have_to_change_variable_at_layer(5, 5))
        self.assertTrue(main.have_to_change_variable_at_layer(10, 5))
        self.assertTrue(main.have_to_change_variable_at_layer(25, 5))

    def test_is_changing_only_extruder(self):
        self.assertFalse(main.is_changing_only_extruder('G92 E0'))
        self.assertFalse(main.is_changing_only_extruder('G1 X134.432 Y103.996 E0.05422'))
        self.assertTrue(main.is_changing_only_extruder('G1 F2700 E-5'))
        self.assertTrue(main.is_changing_only_extruder('G1 F2700 E7.6531'))

    def test_get_extruder_position(self):
        self.assertEqual(main.get_extruder_position('G1 F1200 X133.539 Y103.864 E0.02712'), 0.02712)
        self.assertEqual(main.get_extruder_position('G1 F2700 E0'), 0)
        self.assertEqual(main.get_extruder_position('G1 F2700 E-2'), -2)
        self.assertEqual(main.get_extruder_position('G1 F600 X128.835 Y119.171 E193.50153'), 193.50153)
        self.assertEqual(main.get_extruder_position('G1 F600 X128.835 Y119.171 E193.50153'), 193.50153)
        self.assertEqual(main.get_extruder_position('G1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line'), 15)
        self.assertEqual(main.get_extruder_position('G92 E0 ; Reset Extruder'), 0)
        self.assertEqual(main.get_extruder_position('G1 X5 Y20 Z0.3 F5000.0 ; Move over to prevent blob squish'), None)

    def test_is_printing(self):
        self.assertTrue(main.is_printing('G1 F1200 X133.539 Y103.864 E0.02712'))
        self.assertTrue(main.is_printing('G1 X136.166 Y104.495 E0.10843'))
        self.assertFalse(main.is_printing('G0 F6000 X132.637 Y103.811 Z0.2'))
        self.assertFalse(main.is_printing('G1 F2700 E0'))


if __name__ == '__main__':
    unittest.main()