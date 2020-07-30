import sys


def main():
    # TODO safety measures for changing this.
    # TODO changing the argument parsing mechanism
    filename = sys.argv[1]
    layer_distance = int(sys.argv[2])
    initial_retraction_distance = int(sys.argv[3])

    gcode_source = open(filename, "r")
    gcode_target = open(filename + ".mod", "w+")

    current_retraction_distance_at = initial_retraction_distance
    current_layer_at = None
    currently_extruder_at = None

    lines = gcode_source.readlines()
    for line in lines:

        if get_current_layer(line) is not None:
            current_layer_at = get_current_layer(line)
            log_layer_line(current_layer_at)
            # We increment retraction distance if required
            if not_initial_layer(current_layer_at) and have_to_change_variable_at_layer(current_layer_at, layer_distance):
                current_retraction_distance_at += 1

        if current_layer_at is not None and currently_extruder_at is not None:
            # Changing the retraction setting derived from the original
            if is_changing_only_extruder(line):
                new_extruder_at = get_extruder_position(line)
                # Check if this is a real extraction
                # TODO do we need to change negative extractions?
                if is_not_negative_extrusion(new_extruder_at) and is_retraction(new_extruder_at, currently_extruder_at):
                    # We recalculate the extrusion value
                    retracted_extruder_at = round(currently_extruder_at - current_retraction_distance_at, 5)
                    log_retraction_change(new_extruder_at, retracted_extruder_at, current_retraction_distance_at,
                                          line, current_layer_at)
                    line = line.replace(str(new_extruder_at), str(retracted_extruder_at))

        if is_printing(line):
            currently_extruder_at = get_extruder_position(line)

        gcode_target.writelines(line)


def log_retraction_change(new_extruder_at, retracted_extruder_at, current_retraction_distance_at,
                          line, current_layer_at):
    print('RETRACT: ' + str(new_extruder_at) + ' changed to ' + str(
        retracted_extruder_at) + ' with retraction distance ' + str(
        current_retraction_distance_at) + 'mm in ' + line + ' at layer ' + str(current_layer_at))


def log_layer_line(current_layer):
    print('LAYER:' + str(current_layer))


def get_current_layer(line, layer_keyword='LAYER:'):
    """
    Cura adds the current layer into the gcode as a comment. Example:
    ;LAYER:112
    """
    if layer_keyword not in line:
        return None
    position = line.find(layer_keyword)
    position += len(layer_keyword)
    current_layer = int(line[position:])
    return current_layer


def not_initial_layer(layer):
    return layer != 0


def have_to_change_variable_at_layer(layer, steps):
    return layer % steps == 0


def is_changing_only_extruder(line):
    """
    The lines which position only the extruder can be retraction commands:
    G1 F2700 E-5
    """
    return line.startswith('G1 ') and 'F' in line and 'E' in line and 'X' not in line and 'Y' not in line


def is_printing(line):
    """
    The lines which are not just moving the head are formatted as following.
    The F value is changing the movement speed according to the documentation.
    G1 X140.481 Y107.67 E0.2711
    G1 X141.011 Y108.401 E0.2982
    G1 X141.473 Y109.177 E0.32531
    G1 F1200 X133.539 Y103.864 E0.02712
    """
    return line.startswith('G1 ') and 'X' in line and 'Y' in line and 'E' in line


def is_not_negative_extrusion(extruder_position):
    return extruder_position > 0


def is_retraction(new_extruder_position, old_extruder_position):
    return new_extruder_position < old_extruder_position


def get_extruder_position(line):
    """
    Get the current extruder position from the line. Example for position set to 0.02712:
    G1 F1200 X133.539 Y103.864 E0.02712
    """
    tokens = line.split()
    for token in tokens:
        if 'E' in token:
            position = token.find('E')
            position += 1
            return float(token[position:])
    return None


if __name__ == "__main__":
    main()
