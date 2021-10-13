import numpy as np
import seaborn as sns
from typing import List, Tuple


PRIMARY = "#4ac5db"
PURPLE = "#9554ff"
DARK_BLUE = "#254c7a"
BLUE = "#276ef2"
BASE_COLORS = [DARK_BLUE, PURPLE, BLUE, PRIMARY]


def hex_to_rgb(hex_color: str) -> Tuple[int]:
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color: Tuple[int]) -> str:
    MIN = 0
    MAX = 255
    return "#" + "".join(
        "{:02x}".format(np.clip(x, MIN, MAX))
        for x in rgb_color
    )


def normalize_rgb(rgb_color: Tuple[int]) -> Tuple[float]:
    return tuple(x/255 for x in rgb_color)


def denormalize_rgb(rgb_color: Tuple[float]) -> Tuple[int]:
    return tuple(int(x*255) for x in rgb_color)


def generate_gradient_palette(from_color: str, to_color: str, n_colors: int = 256) -> List[str]:
    from_color_rgb = normalize_rgb(hex_to_rgb(from_color))
    to_color_rgb = normalize_rgb(hex_to_rgb(to_color))

    palette = sns.blend_palette([from_color_rgb, to_color_rgb], n_colors=n_colors)
    return [rgb_to_hex(denormalize_rgb(color)) for color in palette]


def generate_categorical_palette(base_colors: List[str] = BASE_COLORS) -> List[str]:
    lighter_palettes = [sns.light_palette(normalize_rgb(hex_to_rgb(hex_color))) for hex_color in base_colors]
    return [
        rgb_to_hex(denormalize_rgb(color))
        for palette in list(zip(*lighter_palettes))[::-2]
        for color in palette
    ]
