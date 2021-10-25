import itertools
import numpy as np
import seaborn as sns
from typing import Iterable, List, Tuple


TURQUOISE = "#4ac5db"
DARK_TURQUOISE = "#0a9e9e"
LIGHT_TURQUOISE = "#c3ecf4"
PURPLE = "#9554ff"
DARK_BLUE = "#254c7a"
BLUE = "#276ef2"
BASE_COLORS = [DARK_BLUE, PURPLE, BLUE, TURQUOISE]


def hex_to_rgb(hex_color: str) -> Tuple[int]:
    """Converts Hex color to RGB.

    Args:
        hex_color (str): Hex color (e.g. "#4ac5db").

    Returns:
        Tuple[int]: RGB color (e.g. (10, 154, 130)).
    """
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color: Tuple[int]) -> str:
    """Converts RGB color to Hex.

    Args:
        rgb_color (Tuple[int]): RGB color (e.g. (10, 154, 130)).

    Returns:
        str: Hex color (e.g. "#4ac5db").
    """
    MIN = 0
    MAX = 255
    return "#" + "".join(
        "{:02x}".format(np.clip(x, MIN, MAX))
        for x in rgb_color
    )


def normalize_rgb(rgb_color: Tuple[int]) -> Tuple[float]:
    """Normalizes RGB color so its components will range from 0 to 1.

    Args:
        rgb_color (Tuple[int]): RGB color (e.g. (10, 154, 130)).

    Returns:
        Tuple[float]: RGB color (e.g. (10/255, 154/255, 130/255)).
    """
    return tuple(x/255 for x in rgb_color)


def denormalize_rgb(rgb_color: Tuple[float]) -> Tuple[int]:
    """Denormalizes RGB color so its components will range from 0 to 255.

    Args:
        rgb_color (Tuple[int]): RGB color (e.g. (10/255, 154/255, 130/255)).

    Returns:
        Tuple[float]: RGB color (e.g. (10, 154, 130)).
    """
    return tuple(int(x*255) for x in rgb_color)


def generate_continuous_palette(from_color: str, to_color: str, n_colors: int = 256) -> List[str]:
    """Generates a continuous color palette of two given colors.

    Args:
        from_color (str): Hex color to start the palette.
        to_color (str): Hex color to end the palette.
        n_colors (int, optional): Number of colors to include in the resulting palette. Defaults to 256.

    Returns:
        List[str]: A continuous color palette.
    """
    from_color_rgb = normalize_rgb(hex_to_rgb(from_color))
    to_color_rgb = normalize_rgb(hex_to_rgb(to_color))

    palette = sns.blend_palette([from_color_rgb, to_color_rgb], n_colors=n_colors)
    return [rgb_to_hex(denormalize_rgb(color)) for color in palette]


def generate_categorical_palette(base_colors: List[str] = BASE_COLORS) -> List[str]:
    """Generates a categorical color palette given a list of base colors.

    The function adds lighter shades of the base colors so the resulting palette includes
    the base colors and their light shades.

    Args:
        base_colors (List[str], optional): Hex colors. Defaults to BASE_COLORS.

    Returns:
        List[str]: A categorical palette.
    """
    lighter_palettes = [sns.light_palette(normalize_rgb(hex_to_rgb(hex_color))) for hex_color in base_colors]
    return [
        rgb_to_hex(denormalize_rgb(color))
        for palette in list(zip(*lighter_palettes))[::-2]
        for color in palette
    ]


def make_palette_cyclic(palette: Iterable[str]) -> Iterable[str]:
    """Returns a periodic infinite palette.

    Args:
        palette (Iterable[str]): A finite palette.

    Returns:
        Iterable[str]: An infinite palette.
    """
    return itertools.cycle(palette)
