"""Tests for virplot.settings."""

import textwrap

from virplot.settings import Settings, load_settings


def test_load_settings_full(tmp_path):
    yml = tmp_path / "spec.yml"
    yml.write_text(textwrap.dedent("""\
        color_mapping:
          RdRp: '#ff0000'
          CP: '#00ff00'
        default_color: '#aaaaaa'
        depth_line_color: '#0000ff'
        shade_color: '#ff6666'
        annotation_fontsize: 12
        stacked_area_colors:
          - '#111111'
          - '#222222'
        legend_location: "lower right"
        title: "My Plot"
    """))
    s = load_settings(str(yml))
    assert s.color_mapping == {"RdRp": "#ff0000", "CP": "#00ff00"}
    assert s.default_color == "#aaaaaa"
    assert s.depth_line_color == "#0000ff"
    assert s.annotation_fontsize == 12
    assert s.legend_location == "lower right"
    assert s.title == "My Plot"
    assert len(s.stacked_area_colors) == 2


def test_load_settings_defaults(tmp_path):
    yml = tmp_path / "empty.yml"
    yml.write_text("")
    s = load_settings(str(yml))
    assert s == Settings()


def test_load_settings_partial(tmp_path):
    yml = tmp_path / "partial.yml"
    yml.write_text("annotation_fontsize: 14\n")
    s = load_settings(str(yml))
    assert s.annotation_fontsize == 14
    assert s.default_color == Settings.default_color
