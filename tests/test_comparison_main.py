import unittest
import main

GCODE_FILE = 'tests/CE3_stringing.gcode'
GCODE_FILE_MODIFIED = 'tests/CE3_stringing.gcode' + ".mod"


def filter_retraction_speed_differing(lines):
    """
    Removing the final retraction because it's different from the one configured (added by Cura).
    Should look like this: G1 E-2 Z0.2 F2700 ;Retract and raise Z
    """
    lines = list(filter(lambda line: ' ;Retract and raise Z' not in line, lines))
    return lines


class ComparisonTestMain(unittest.TestCase):

    def test_comparing_generated_file_with_retraction_distance(self):
        # Executing retraction distance change
        gcode_source = open(GCODE_FILE, "r")
        gcode_target = open(GCODE_FILE_MODIFIED, "w+")
        main.change_retraction_distance(
            gcode_source,
            gcode_target,
            initial_retraction_distance=0,
            retraction_distance_step=1.0,
            layer_distance=25
        )
        gcode_target.flush()
        gcode_source.close()
        gcode_target.close()
        # Verifying
        gcode_result = open(GCODE_FILE_MODIFIED, "r")
        gcode_expected = open('tests/CE3_stringing_retract_0_to_4.gcode', "r")
        lines_result = gcode_result.readlines()
        lines_expected = gcode_expected.readlines()
        self.assertEqual(lines_expected, lines_result, " -- lines should match")
        gcode_expected.close()
        gcode_result.close()

    def test_comparing_generated_file_with_identity_operation_on_distance(self):
        # Executing retraction distance change
        gcode_source = open(GCODE_FILE, "r")
        gcode_target = open(GCODE_FILE_MODIFIED, "w+")
        main.change_retraction_distance(
            gcode_source,
            gcode_target,
            initial_retraction_distance=5,
            retraction_distance_step=0,
            layer_distance=25
        )
        gcode_target.flush()
        gcode_source.close()
        gcode_target.close()
        # Verifying
        gcode_result = open(GCODE_FILE_MODIFIED, "r")
        gcode_expected = open(GCODE_FILE, "r")
        lines_result = gcode_result.readlines()
        lines_expected = gcode_expected.readlines()
        self.assertEqual(lines_expected, lines_result, " -- lines should match")
        gcode_expected.close()
        gcode_result.close()

    def test_comparing_generated_file_with_retraction_speed(self):
        # Executing retraction distance change
        gcode_source = open(GCODE_FILE, "r")
        gcode_target = open(GCODE_FILE_MODIFIED, "w+")
        main.change_retraction_speed(
            gcode_source,
            gcode_target,
            initial_retraction_speed=1500,
            retraction_speed_steps=300,
            layer_distance=25
        )
        gcode_target.flush()
        gcode_source.close()
        gcode_target.close()
        # Verifying
        gcode_result = open(GCODE_FILE_MODIFIED, "r")
        gcode_expected = open('tests/CE3_stringing_retract_2mm_speed_25-45.gcode', "r")
        lines_result = gcode_result.readlines()
        lines_expected = gcode_expected.readlines()
        self.assertEqual(lines_expected, lines_result, " -- lines should match")
        gcode_expected.close()
        gcode_result.close()

    def test_comparing_generated_file_with_identity_operation_on_speed(self):
        # Executing retraction distance change
        gcode_source = open(GCODE_FILE, "r")
        gcode_target = open(GCODE_FILE_MODIFIED, "w+")
        main.change_retraction_speed(
            gcode_source,
            gcode_target,
            initial_retraction_speed=2700,
            retraction_speed_steps=0,
            layer_distance=25
        )
        gcode_target.flush()
        gcode_source.close()
        gcode_target.close()
        # Verifying
        gcode_result = open(GCODE_FILE_MODIFIED, "r")
        gcode_expected = open(GCODE_FILE, "r")
        lines_result = gcode_result.readlines()
        lines_expected = gcode_expected.readlines()
        lines_result = filter_retraction_speed_differing(lines_result)
        lines_expected = filter_retraction_speed_differing(lines_expected)
        self.assertEqual(lines_expected, lines_result, " -- lines should match")
        gcode_expected.close()
        gcode_result.close()


if __name__ == '__main__':
    unittest.main()
