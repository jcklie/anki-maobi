""" This script creates the background hanzi grids. The coordinates need to be computed in this
complicated way, as the stroke width needs to be taken into account.
"""

import svgwrite

BORDER_COLOR = svgwrite.rgb(0, 0, 0)
BORDER_STROKE_WIDTH = 1

GRID_COLOR = svgwrite.rgb(0xDC, 0xDC, 0xDC)
GRID_STROKE_WIDTH = 0.5
SIZE = 100

def field():
    dwg = svgwrite.Drawing('maobi/field.svg', profile='tiny', size=(SIZE, SIZE))
    dwg.add(dwg.line((SIZE / 2, 0), (SIZE / 2, SIZE), stroke=GRID_COLOR, stroke_width=GRID_STROKE_WIDTH))
    dwg.add(dwg.line((0, SIZE / 2), (SIZE, SIZE / 2), stroke=GRID_COLOR, stroke_width=GRID_STROKE_WIDTH))

    dwg.save()

def rice():
    o = GRID_STROKE_WIDTH / 2
    dwg = svgwrite.Drawing('maobi/rice.svg', profile='tiny', size=(SIZE, SIZE))
    dwg.add(dwg.line((o, o), (SIZE - o, SIZE - o), stroke=GRID_COLOR, stroke_width=GRID_STROKE_WIDTH))
    dwg.add(dwg.line((o, SIZE - o), (SIZE - o, o), stroke=GRID_COLOR, stroke_width=GRID_STROKE_WIDTH))
    dwg.add(dwg.line((SIZE / 2, 0), (SIZE / 2, SIZE), stroke=GRID_COLOR, stroke_width=GRID_STROKE_WIDTH))
    dwg.add(dwg.line((0, SIZE / 2), (SIZE, SIZE / 2), stroke=GRID_COLOR, stroke_width=GRID_STROKE_WIDTH))

    dwg.save()

if __name__ == "__main__":
    field()
    rice()