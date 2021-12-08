import pytest
from mz_bokeh_package.utilities.colors import (
    TURQUOISE,
    DARK_TURQUOISE,
    PURPLE,
    BLUE,
    hex_to_rgb,
    rgb_to_hex,
    normalize_rgb,
    denormalize_rgb,
    make_palette_cyclic,
)

hex_to_rgb_params = [
    (TURQUOISE, (106, 206, 206)),
    (DARK_TURQUOISE, (10, 158, 158)),
    (PURPLE, (149, 84, 255)),
]
normalize_rgb_params = [
    ((255, 255, 255), (1, 1, 1)),
    ((0, 0, 0), (0, 0, 0)),
    ((30, 45, 12), (30/255, 45/255, 12/255)),
]
make_palette_cyclic_params = [
    ([TURQUOISE, PURPLE], 3),
    ([TURQUOISE, PURPLE], 10),
    ([TURQUOISE, PURPLE, DARK_TURQUOISE, BLUE], 3),
]


@pytest.mark.parametrize("hex, expected_rgb", hex_to_rgb_params)
def test_hex_to_rgb(hex, expected_rgb):
    assert hex_to_rgb(hex) == expected_rgb


@pytest.mark.parametrize("expected_hex, rgb", hex_to_rgb_params)
def test_rgb_to_hex(expected_hex, rgb):
    assert rgb_to_hex(rgb) == expected_hex


@pytest.mark.parametrize("rgb, expected_normalized_rgb", normalize_rgb_params)
def test_normalize_rgb(rgb, expected_normalized_rgb):
    assert normalize_rgb(rgb) == expected_normalized_rgb


@pytest.mark.parametrize("expected_denormalized_rgb, rgb", normalize_rgb_params)
def test_denormalize_rgb(expected_denormalized_rgb, rgb):
    assert denormalize_rgb(rgb) == expected_denormalized_rgb


@pytest.mark.parametrize("palette, size", make_palette_cyclic_params)
def test_make_palette_cyclic(palette, size):
    colors_num = len(palette)
    expected_result = palette * int(size / colors_num) + palette[:(size % colors_num)]
    colors_pool = make_palette_cyclic(palette)

    assert [next(colors_pool) for i in range(size)] == expected_result
