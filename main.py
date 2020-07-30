import sys
import argparse


def init_argparse():
    parser = argparse.ArgumentParser(
       description="Change retraction speed or retraction distance gradually by a specific layer height in gcode files"
    )
    parser.add_argument('-m', '--mode', required=True, choices=['speed', 'distance'],
                    help="defines the type of retraction change to apply to the gcode")

    parser.add_argument('-f', '--file', required=True, type=str,
                    help="defines the source gcode file location")

    parser.add_argument('-l', '--layer_step', required=True, type=int,
                    help="defines the layer step")

    parser.add_argument('-d', '--initial_retraction_distance', type=int,
                    help="defines the initial retraction distance")

    parser.add_argument('-ds', '--retraction_distance_step', type=float, default=1.0,
                    help="defines the retraction speed step")

    parser.add_argument('-s', '--initial_retraction_speed', type=int,
                    help="defines the initial retraction speed")

    parser.add_argument('-t', '--retraction_speed_step', type=int,
                    help="defines the retraction speed step")

    return parser.parse_args()


def main():
    # TODO safety measures for changing this.
    # TODO changing the argument parsing mechanism
    args = init_argparse()
    gcode_source = open(args.file, "r")
    gcode_target = open(args.file + ".mod", "w+")

    if 'distance' == args.mode:
        change_retraction_distance(gcode_source=gcode_source, gcode_target=gcode_target,
                                   initial_retraction_distance=args.initial_retraction_distance,
                                   retraction_distance_step=args.retraction_distance_step,
                                   layer_distance=args.layer_step)

    elif 'speed' == args.mode:
        change_retraction_speed(gcode_source=gcode_source, gcode_target=gcode_target,
                                initial_retraction_speed=args.initial_retraction_speed,
                                retraction_speed_steps=args.retraction_speed_step,
                                layer_distance=args.layer_step)


def change_retraction_speed(gcode_source=None,
                            gcode_target=None,
                            initial_retraction_speed=None,
                            retraction_speed_steps=None,
                            layer_distance=None):
    """
    Changing retraction speed for a specific source file. User has to define the initial distance
    and the layer distance, which specifies the number of layers between steps.
    """
    current_retraction_speed_at = initial_retraction_speed
    current_layer_at = None
    currently_extruder_at = None
    lines = gcode_source.readlines()
    for line in lines:

        if get_current_layer(line) is not None:
            current_layer_at = get_current_layer(line)
            log_layer_line(current_layer_at)
            # We increment retraction distance if required
            if not_initial_layer(current_layer_at) and have_to_change_variable_at_layer(current_layer_at,
                                                                                        layer_distance):
                current_retraction_speed_at += retraction_speed_steps

        if current_layer_at is not None and currently_extruder_at is not None:
            # Changing the retraction setting derived from the original
            if is_changing_only_extruder(line):
                feed_rate = get_feed_rate(line)
                log_retraction_speed_change(current_retraction_speed_at=current_retraction_speed_at,
                                            feed_rate=feed_rate,
                                            line=line)
                line = line.replace(str(feed_rate), str(current_retraction_speed_at))

        if is_printing(line):
            currently_extruder_at = get_extruder_position(line)

        gcode_target.writelines(line)


def change_retraction_distance(gcode_source=None,
                               gcode_target=None,
                               initial_retraction_distance=None,
                               retraction_distance_step=None,
                               layer_distance=None):
    """
    Changing retraction distance for a specific source file. User has to define the initial distance
    and the layer distance, which specifies the number of layers between steps.
    """
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
                current_retraction_distance_at += retraction_distance_step

        if current_layer_at is not None and currently_extruder_at is not None:
            # Changing the retraction setting derived from the original
            if is_changing_only_extruder(line):
                new_extruder_at = get_extruder_position(line)
                # Check if this is a real extraction
                # TODO do we need to change negative extractions?
                if is_not_negative_extrusion(new_extruder_at) and is_retraction(new_extruder_at, currently_extruder_at):
                    # We recalculate the extrusion value
                    retracted_extruder_at = round(currently_extruder_at - current_retraction_distance_at, 5)
                    log_retraction_distance_change(new_extruder_at=new_extruder_at,
                                                   retracted_extruder_at=retracted_extruder_at,
                                                   current_retraction_distance_at=current_retraction_distance_at,
                                                   current_layer_at=current_layer_at,
                                                   line=line)
                    line = line.replace(str(new_extruder_at), str(retracted_extruder_at))

        if is_printing(line):
            currently_extruder_at = get_extruder_position(line)

        gcode_target.writelines(line)


def log_retraction_speed_change(current_retraction_speed_at=None, feed_rate=None, line=None):
    print(f'RETRACT: Changing speed from {feed_rate} => {current_retraction_speed_at} in line {line}')


def log_retraction_distance_change(new_extruder_at=None,
                                   retracted_extruder_at=None,
                                   current_retraction_distance_at=None,
                                   current_layer_at=None,
                                   line=None):
    print(f'RETRACT: {new_extruder_at} changed to {retracted_extruder_at}'
          f' with retraction distance {current_retraction_distance_at}mm'
          f' in line {line} at layer {current_layer_at}')


def log_layer_line(current_layer):
    print(f'LAYER:{current_layer}')


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


def get_feed_rate(line):
    """
    Get the current feed rate from the line. Example for 1200:
    G1 F1200 X133.539 Y103.864 E0.02712
    """
    tokens = line.split()
    for token in tokens:
        if 'F' in token:
            position = token.find('F')
            position += 1
            return int(token[position:])
    return None


if __name__ == "__main__":
    main()
