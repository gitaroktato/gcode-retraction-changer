import unittest
import main


class ComparisonTestMain(unittest.TestCase):

    def test_comparing_generated_file(self):
        gcode_source = open('tests/CE3_stringing.gcode', "r")
        gcode_target = open('tests/CE3_stringing.gcode' + ".mod", "w+")
        main.change_retraction_distance(
            gcode_source,
            gcode_target,
            initial_retraction_distance=0,
            retraction_distance_step=1.0,
            layer_distance=25
        )
        gcode_target.flush()
        gcode_result = open('tests/CE3_stringing.gcode' + ".mod", "r")
        gcode_expected = open('tests/CE3_stringing_retract_0_to_4.gcode', "r")
        lines_result = gcode_result.readlines()
        lines_expected = gcode_expected.readlines()
        self.assertEqual(lines_expected, lines_result, " -- lines should match")


if __name__ == '__main__':
    unittest.main()
