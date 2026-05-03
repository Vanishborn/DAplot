"""YAML settings loader."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import yaml

log = logging.getLogger(__name__)

_KNOWN_KEYS = {
    "color_mapping", "default_color", "depth_line_color", "shade_color",
    "annotation_fontsize", "stacked_area_colors", "legend_location", "title",
}


@dataclass
class Settings:
    color_mapping: dict[str, str] = field(default_factory=dict)
    default_color: str = "#9F9F9F"
    depth_line_color: str = "blue"
    shade_color: str = "tomato"
    annotation_fontsize: int = 8
    stacked_area_colors: list[str] = field(default_factory=list)
    legend_location: str = "upper left"
    title: str = ""


def load_settings(yaml_path: str) -> Settings:
    """Load a YAML spec file and return a Settings instance."""
    with open(yaml_path) as fp:
        raw = yaml.safe_load(fp) or {}

    unknown = set(raw) - _KNOWN_KEYS
    if unknown:
        log.warning("Unknown YAML keys ignored: %s", ", ".join(sorted(unknown)))

    missing = _KNOWN_KEYS - set(raw)
    if missing:
        log.info("Using defaults for missing YAML keys: %s", ", ".join(sorted(missing)))

    return Settings(
        color_mapping=raw.get("color_mapping", {}),
        default_color=raw.get("default_color", Settings.default_color),
        depth_line_color=raw.get("depth_line_color", Settings.depth_line_color),
        shade_color=raw.get("shade_color", Settings.shade_color),
        annotation_fontsize=raw.get("annotation_fontsize", Settings.annotation_fontsize),
        stacked_area_colors=raw.get("stacked_area_colors", []),
        legend_location=raw.get("legend_location", Settings.legend_location),
        title=raw.get("title", Settings.title),
    )
