from string import Template

from anki.cards import Card

from .config import MaobiConfig
from .data import _get_character, _load_character_data
from .grid import build_hanzi_grid, get_border_style
from .util import error

_TARGET_DIV = "maobi-annotation-target-div"

TEMPLATE = Template(
    """
$html

<style scoped>
$styles
</style>

<script>
onShownHook.push(function () {
    var writer = HanziWriter.create('$target_div', '$character', {
    width: $size,
    height: $size,
    delayBetweenLoops: 3000,
    charDataLoader: function(char, onComplete) {
    var charData = $character_data;
        onComplete(charData);
    }
    });
    writer.loopCharacterAnimation();
});
</script>
"""
)


def draw_looping_animation(html: str, card: Card, config: MaobiConfig) -> str:
    if 'id="' + _TARGET_DIV not in html:
        return html

    # Get the character to loop and the corresponding character data
    character = _get_character(card, config)
    character_data = _load_character_data(character)

    with open(r"D:\AnkiData\addons21\maobi\foo.html", "w", encoding="utf-8") as f:
        f.write(html)

    styles = [
        get_border_style(_TARGET_DIV),
        build_hanzi_grid(_TARGET_DIV, config.grid)
    ]

    # Render the template
    data = {
        "html": html,
        "target_div": _TARGET_DIV,
        "character": character,
        "character_data": character_data,
        "size": config.size,
        "styles": "\n".join(styles),
    }

    result = TEMPLATE.substitute(data)

    return result






