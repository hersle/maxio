#!/usr/bin/env python3
#
# Script for converting reMarkable tablet ".rm" files to SVG image.
# this works for the new *.rm format, where each page is a seperate file
# credit for updating to version 5 rm files goes to
# https://github.com/peerdavid/rmapi/blob/master/tools/rM2svg
import sys
import struct
import os.path
import argparse


__prog_name__ = "rm2svg"
__version__ = "0.0.2"


# Size
default_width = 1404
default_height = 1872

# Mappings
stroke_colour = {
    0: [0, 0, 0],
    1: [125, 125, 125],
    2: [255, 255, 255]
}


'''stroke_width={
    0x3ff00000 : 2,
    0x40000000 : 4,
    0x40080000 : 8,
}'''


def main():
    parser = argparse.ArgumentParser(prog=__prog_name__)
    parser.add_argument('--height',
                        help='Desired height of image',
                        type=float,
                        default=default_height)
    parser.add_argument('--width',
                        help='Desired width of image',
                        type=float,
                        default=default_width)
    parser.add_argument("-i",
                        "--input",
                        help=".rm input file",
                        required=True,
                        metavar="FILENAME",
                        # type=argparse.FileType('r')
                        )
    parser.add_argument("-o",
                        "--output",
                        help="prefix for output files",
                        required=True,
                        metavar="NAME",
                        # type=argparse.FileType('w')
                        )
    parser.add_argument("-c",
                        "--coloured_annotations",
                        help="Colour annotations for document markup.",
                        action='store_true',
                        )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    if not os.path.exists(args.input):
        parser.error(f'The file "{args.input}" does not exist!')
    if args.coloured_annotations:
        set_coloured_annots()
    rm2svg(args.input, args.output, args.coloured_annotations,
           args.width, args.height)


def set_coloured_annots():
    global stroke_colour
    stroke_colour = {
        0: [0, 0, 0],
        1: [255, 0, 0],
        2: [255, 255, 255],
        3: [150, 0, 0],
        4: [0, 0, 125]
    }


def abort(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


class Segment():
    def __init__(self, _id, xpos, ypos, speed, tilt, width, pressure):
        self.id = _id
        self.xpos = xpos
        self.ypos = ypos
        self.speed = speed
        self.tilt = tilt
        self.width = width
        self.pressure = pressure


class Stroke():
    def __init__(self, _id, pen, color, width, opacity):
        self.id = _id
        self.pen = pen
        self.color = color
        self.width = width
        self.opacity = opacity
        self.segments = []

    def append_segment(self, segment):
        self.segments.append(segment)


class Layer():
    def __init__(self, _id):
        self.id = _id
        self.strokes = []
        pass

    def append_stroke(self, stroke):
        self.strokes.append(stroke)


class Page():
    def __init__(self):
        self.layers = []
        pass

    def append_layer(self, layer):
        self.layers.append(layer)


def rm2svg(input_file, output_name, coloured_annotations=False,
           width=default_width, height=default_height):

    if coloured_annotations:
        set_coloured_annots()

    page = parse_rm_input(input_file, coloured_annotations)
    convert_to_svg(page, output_name, width, height)


def parse_rm_input(input_file, coloured_annotations):
    with open(input_file, 'rb') as f:
        data = f.read()
    offset = 0

    # Is this a reMarkable .lines file?
    expected_header_v3 = b'reMarkable .lines file, version=3          '
    expected_header_v5 = b'reMarkable .lines file, version=5          '
    if len(data) < len(expected_header_v5) + 4:
        abort('File too short to be a valid file')

    fmt = f'<{len(expected_header_v5)}sI'
    header, nlayers = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
    is_v3 = (header == expected_header_v3)
    is_v5 = (header == expected_header_v5)
    if (not is_v3 and not is_v5) or nlayers < 1:
        abort(f'Not a valid reMarkable file: <header={header}><nlayers={nlayers}>')
        return

    page = Page()

    for layer_id in range(nlayers):
        fmt = '<I'
        (nstrokes,) = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702

        layer = Layer(layer_id)

        # Iterate through the strokes in the layer (If there is any)
        for stroke_id in range(nstrokes):
            if is_v3:
                fmt = '<IIIfI'
                pen_nr, colour, i_unk, width, nsegments = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
            if is_v5:
                fmt = '<IIIffI'
                pen_nr, colour, i_unk, width, unknown, nsegments = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
                # print(f'Stroke {stroke}: pen_nr={pen_nr}, colour={colour}, width={width}, unknown={unknown}, nsegments={nsgiments}')

            opacity = 1
            # print(pen_nr)
            # Brush
            if (pen_nr == 0 or pen_nr == 12):
                pen = Brush(width, colour)
            # caligraphy
            elif pen_nr == 21:
                pen = Caligraphy(width, colour)
            # Marker
            elif (pen_nr == 3 or pen_nr == 16):
                pen = Marker(width, colour)
            # BallPoint
            elif (pen_nr == 2 or pen_nr == 15):
                if coloured_annotations:
                    colour = 4
                pen = Ballpoint(width, colour)
            # Fineliner
            elif (pen_nr == 4 or pen_nr == 17):
                pen = Fineliner(width, colour)
            # pencil
            elif (pen_nr == 1 or pen_nr == 14):
                pen = Pencil(width, colour)
            # mech
            elif (pen_nr == 7 or pen_nr == 13):
                pen = Mechanical_Pencil(width, colour)
            # Highlighter
            elif (pen_nr == 5 or pen_nr == 18):
                width = 15
                opacity = 0.2
                if coloured_annotations:
                    colour = 3
                pen = Highlighter(width, colour)
            elif (pen_nr == 8):  # Erase area
                pen = Erase_Area(width, colour)
            elif (pen_nr == 6):  # Eraser
                colour = 2
                pen = Eraser(width, colour)
            else:
                print(f'Unknown pen_nr: {pen_nr}')

            stroke = Stroke(stroke_id, pen, stroke_colour[colour], width, opacity)

            # Iterate through the segments
            for segment_id in range(nsegments):
                fmt = '<ffffff'
                xpos, ypos, speed, tilt, width, pressure = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
                stroke.append_segment(Segment(segment_id, xpos, ypos, speed, tilt, width, pressure))

            # store stroke
            layer.append_stroke(stroke)

        # store layer
        page.append_layer(layer)

    return page


def convert_to_svg(page, output_name, width, height):
    svg_header = '''
    <script type="application/ecmascript"> <![CDATA[
        var visiblePage = 'p1';
        function goToPage(page) {
            document.getElementById(visiblePage).setAttribute('style', 'display: none');
            document.getElementById(page).setAttribute('style', 'display: inline');
            visiblePage = page;
        }
    ]]>
    </script>
    '''
    with open(output_name, 'w') as output:
        # BEGIN Notebook
        output.write(f'<svg xmlns="http://www.w3.org/2000/svg" height="{height}" width="{width}">')
        output.write(svg_header + '\n')

        # Iterate through pages (There is at least one)
        output.write('    <g id="p1" style="display:inline">\n')
        output.write('        <filter id="blurMe"><feGaussianBlur in="SourceGraphic" stdDeviation="10" /></filter>\n')

        for layer in page.layers:
            # Iterate through the strokes in the layer (If there is any)
            output.write(f'        <!-- layer: {layer.id} --> \n')
            for stroke in layer.strokes:
                last_x = -1.
                last_y = -1.
                last_width = 0
                # BEGIN stroke
                output.write(f'        <!-- stroke: {stroke.id} pen: "{stroke.pen.name}" --> \n')
                output.write('        <polyline ')
                output.write(f'style="fill:none;stroke:{stroke.color};stroke-width:{stroke.width};opacity:{stroke.opacity}" ')
                output.write(f'stroke-linecap="{stroke.pen.stroke_cap}" ')

                output.write('points="')

                last_x = -1.
                last_y = -1.
                last_width = 0
                # Iterate through the segments to form a polyline
                for segment in stroke.segments:
                    # output.write(f'        <!-- segment: {segment.id} --> \n')
                    ratio = (height/width)/(1872/1404)
                    if ratio > 1:
                        segment.xpos = ratio*((segment.xpos*width)/1404)
                        segment.ypos = (segment.ypos*height)/1872
                    else:
                        segment.xpos = (segment.xpos*width)/1404
                        segment.ypos = (1/ratio)*(segment.ypos*height)/1872
                    if segment.id % stroke.pen.segment_length == 0:
                        segment_color = stroke.pen.get_segment_color(segment.speed, segment.tilt, segment.width, segment.pressure, last_width)
                        segment_width = stroke.pen.get_segment_width(segment.speed, segment.tilt, segment.width, segment.pressure, last_width)
                        segment_opacity = stroke.pen.get_segment_opacity(segment.speed, segment.tilt, segment.width, segment.pressure, last_width)
                        # print(segment_color, segment_width, segment_opacity, stroke.pen.stroke_cap)
                        # UPDATE stroke
                        output.write('"/>\n')
                        output.write('        <polyline ')
                        output.write(f'style="fill:none; stroke:{segment_color} ;stroke-width:{segment_width:.3f};opacity:{segment_opacity}" ')
                        output.write(f'stroke-linecap="{stroke.pen.stroke_cap}" ')
                        output.write('points="')
                        if last_x != -1.:
                            # Join to previous segment
                            output.write('{:.3f},{:.3f} '.format(last_x, last_y))

                    last_x = segment.xpos
                    last_y = segment.ypos
                    last_width = segment_width

                    # BEGIN and END polyline segment
                    output.write('{:.3f},{:.3f} '.format(segment.xpos, segment.ypos))

                # END stroke
                output.write('" />\n')

        # Overlay the page with a clickable rect to flip pages
        output.write('\n')
        output.write('        <!-- clickable rect to flip pages -->\n')
        output.write(f'        <rect x="0" y="0" width="{width}" height="{height}" fill-opacity="0"/>\n')
        # Closing page group
        output.write('    </g>\n')
        # END notebook
        output.write('</svg>')
        output.close()


def extract_data(input_file):
    """
    gets stroke information as a list. Useful for figuring out which value does what.
    """

    with open(input_file, 'rb') as f:
        data = f.read()
    offset = 0

    # Is this a reMarkable .lines file?
    expected_header_v3 = b'reMarkable .lines file, version=3          '
    expected_header_v5 = b'reMarkable .lines file, version=5          '
    if len(data) < len(expected_header_v5) + 4:
        abort('File too short to be a valid file')

    fmt = f'<{len(expected_header_v5)}sI'
    header, nlayers = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
    is_v3 = (header == expected_header_v3)
    is_v5 = (header == expected_header_v5)
    if (not is_v3 and not is_v5) or nlayers < 1:
        abort(f'Not a valid reMarkable file: <header={header}><nlayers={nlayers}>')
        return

    my_list = []
    for _ in range(nlayers):
        fmt = '<I'
        (nstrokes,) = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702

        # Iterate through the strokes in the layer (If there is any)
        for _ in range(nstrokes):
            if is_v5:
                fmt = '<IIIffI'
                pen, colour, i_unk, width, i_unk4, nsegments = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
                # print(f'Stroke {stroke}: pen={pen}, colour={colour}, width={width}, unknown={unknown}, nsegments={nsegments}')

            # Iterate through the segments to form a polyline
            for _ in range(nsegments):
                fmt = '<ffffff'
                xpos, ypos, pressure, tilt, i_unk2, i_unk3 = struct.unpack_from(fmt, data, offset); offset += struct.calcsize(fmt)  # noqa: E702
                # xpos += 60
                # ypos -= 20
                my_list.append([pen, colour, i_unk, width, i_unk4, nsegments, xpos, ypos, pressure, tilt, i_unk2, i_unk3])
    return my_list


class Pen:
    def __init__(self, base_width, base_color):
        self.base_width = base_width
        self.base_color = stroke_colour[base_color]
        self.segment_length = 1000
        self.stroke_cap = "round"
        self.base_opacity = 1
        self.name = "Basic Pen"

    def get_segment_width(self, speed, tilt, width, pressure, last_width):
        return self.base_width

    def get_segment_color(self, speed, tilt, width, pressure, last_width):
        return "rgb"+str(tuple(self.base_color))

    def get_segment_opacity(self, speed, tilt, width, pressure, last_width):
        return self.base_opacity

    def cutoff(self, value):
        """must be between 1 and 0"""
        value = 1 if value > 1 else value
        value = 0 if value < 0 else value
        return value


class Fineliner(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.base_width = (base_width ** 2.1) * 1.3
        self.name = "Fineliner"


class Ballpoint(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.segment_length = 5
        self.name = "Ballpoint"

    def get_segment_width(self, speed, tilt, width, pressure, last_width):
        segment_width = (0.5 + pressure) + (1 * width) - 0.5*(speed/50)
        return segment_width

    def get_segment_color(self, speed, tilt, width, pressure, last_width):
        intensity = (0.1 * -(speed / 35)) + (1.2 * pressure) + 0.5
        intensity = self.cutoff(intensity)
        # using segment color not opacity because the dots interfere with each other.
        # Color must be 255 rgb
        segment_color = [int(abs(intensity - 1) * 255)] * 3
        return "rgb"+str(tuple(segment_color))

    # def get_segment_opacity(self, speed, tilt, width, pressure, last_width):
    #     segment_opacity = (0.2 * -(speed / 35)) + (0.8 * pressure)
    #     segment_opacity *= segment_opacity
    #     segment_opacity = self.cutoff(segment_opacity)
    #     return segment_opacity


class Marker(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.segment_length = 3
        self.name = "Marker"

    def get_segment_width(self, speed, tilt, width, pressure, last_width):
        segment_width = 0.9 * (((1 * width)) - 0.4 * tilt) + (0.1 * last_width)
        return segment_width


class Pencil(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.segment_length = 2
        self.name = "Pencil"

    def get_segment_width(self, speed, tilt, width, pressure, last_width):
        segment_width = 0.7 * ((((0.8*self.base_width) + (0.5 * pressure)) * (1 * width)) - (0.25 * tilt**1.8) - (0.6 * speed / 50))
        # segment_width = 1.3*(((self.base_width * 0.4) * pressure) - 0.5 * ((tilt ** 0.5)) + (0.5 * last_width))
        max_width = self.base_width * 10
        segment_width = segment_width if segment_width < max_width else max_width
        return segment_width

    def get_segment_opacity(self, speed, tilt, width, pressure, last_width):
        segment_opacity = (0.1 * -(speed / 35)) + (1 * pressure)
        segment_opacity = self.cutoff(segment_opacity) - 0.1
        return segment_opacity


class Mechanical_Pencil(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.base_width = self.base_width ** 2
        self.base_opacity = 0.7
        self.name = "Mechanical Pencil"


class Brush(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.segment_length = 2
        self.stroke_cap = "round"
        self.opacity = 1
        self.name = "Brush"

    def get_segment_width(self, speed, tilt, width, pressure, last_width):
        segment_width = 0.7 * (((1 + (1.4 * pressure)) * (1 * width)) - (0.5 * tilt) - (0.5 * speed / 50))  # + (0.2 * last_width)
        return segment_width

    def get_segment_color(self, speed, tilt, width, pressure, last_width):
        intensity = (pressure ** 1.5 - 0.2 * (speed / 50)) * 1.5
        intensity = self.cutoff(intensity)
        # using segment color not opacity because the dots interfere with each other.
        # Color must be 255 rgb
        rev_intensity = abs(intensity - 1)
        segment_color = [int(rev_intensity * (255 - self.base_color[0])),
                         int(rev_intensity * (255 - self.base_color[1])),
                         int(rev_intensity * (255 - self.base_color[2]))]

        return "rgb"+str(tuple(segment_color))


class Highlighter(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.stroke_cap = "square"
        self.base_opacity = 0.3
        self.name = "Highlighter"


class Eraser(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.stroke_cap = "square"
        self.base_width = self.base_width * 2
        self.name = "Eraser"


class Erase_Area(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.stroke_cap = "square"
        self.base_opacity = 0
        self.name = "Erase Area"


class Caligraphy(Pen):
    def __init__(self, base_width, base_color):
        super().__init__(base_width, base_color)
        self.segment_length = 2
        self.name = "Calligraphy"

    def get_segment_width(self, speed, tilt, width, pressure, last_width):
        segment_width = 0.9 * (((1 + pressure) * (1 * width)) - 0.3 * tilt) + (0.1 * last_width)
        return segment_width


if __name__ == "__main__":
    main()
