from string import Template
from urllib.parse import quote

from .config import GridType, PATH_RICE_GRID, PATH_FIELD_GRID


def get_border_style(target_div: str) -> str:
    style = Template("""
    #$target_div {
        display: inline-block;
    
        // We use outline instead of border in order to not cut into the background grid image: it 
        // can be that the border stroke width would be divided between inside and outside the div,
        // therefore overlapping with the background.
        outline-color: rgb(0, 0, 0);
        outline-style: solid;
        outline-width: 1px;
        outline-offset: -1px;
    }
    """)
    return style.substitute(target_div=target_div)


def build_hanzi_grid(target_div: str, grid_type: GridType) -> str:
    """ Generate the JavaScript snippet that sets the background specified by `background_type`.

    Right now, legal values for `background_type` are "rice" or "field". The SVG itself is generated
    with `scripts/generate_hanzi_grids.py`.
    """

    backgrounds = {"rice": PATH_RICE_GRID, "field": PATH_FIELD_GRID}

    # Do nothing for unknown background type
    if grid_type.name not in backgrounds:
        return ""

    # We use CSS here to set the style, as it seems the easiest. I considered using inline CSS
    # style directly, but that seemed less maintainable to generate. I also tried
    # `background-size: covered;` , but that made the image cut off at the right side.
    style = Template(
        """
#$target_div {
    background: url('data:image/svg+xml;charset=utf8,$svg_data');
    background-size: 100% 100%;
}
"""
    )

    # Load the SVG data
    with open(backgrounds[grid_type.name]) as f:
        svg_data = f.read()

    return style.substitute(target_div=target_div, svg_data=quote(svg_data))