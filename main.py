import sys


def main():
    LAYER_KEYWORD = 'LAYER:'
    # TODO safety measures for changing this.
    layer_height_for_steps = int(sys.argv[2])
    filename = sys.argv[1]
    initial_retraction_distance = int(sys.argv[3])
    retraction_distance_at = initial_retraction_distance

    gcode_source = open(filename, "r")
    gcode_target = open(filename + ".mod", "w+")
    current_layer = None
    currently_extruder_at = None

    lines = gcode_source.readlines()
    for line in lines:

        if LAYER_KEYWORD in line:
            current_layer = get_current_layer(LAYER_KEYWORD, line)
            print('LAYER: ' + str(current_layer))
            # We increment retraction distance
            if current_layer != 0 and current_layer % layer_height_for_steps == 0:
                retraction_distance_at += 1

        if current_layer is not None:

            if currently_extruder_at is not None:
                # Changing the retraction setting derived from the original
                if line.startswith('G1 ') and 'F' in line and 'E' in line and 'X' not in line and 'Y' not in line:
                    new_extruder_at = get_E_step(line)
                    if 0 < new_extruder_at < currently_extruder_at:
                        retracted_extruder_at = round(currently_extruder_at - retraction_distance_at, 5)
                        print('RETRACT: ' + str(new_extruder_at) + ' changed to ' + str(retracted_extruder_at) + ' with retraction distance ' + str(retraction_distance_at) + 'mm in ' + line + ' at layer ' + str(current_layer))
                        line = line.replace(str(new_extruder_at), str(retracted_extruder_at))

            if line.startswith('G1 ') and 'X' in line and 'Y' in line and 'E' in line:
                currently_extruder_at = get_E_step(line)
                # print('E: ' + str(currently_extruder_at) + ' in line ' + line)

        gcode_target.writelines(line)


def get_current_layer(layer_keyword, line):
    position = line.find(layer_keyword)
    position += len(layer_keyword)
    current_layer = int(line[position:])
    return current_layer


def get_E_step(line):
    tokens = line.split()
    for token in tokens:
        if 'E' in token:
            position = token.find('E')
            position += 1
            currently_extruder_at = float(token[position:])
    return currently_extruder_at


if __name__ == "__main__":
    main()
