"""Deprecated patch for Sanic console coloring."""

import sanic.log


def _old_color_format(self, format_spec: str) -> str:
    return self.value + format_spec


def patch_colors():
    setattr(sanic.log.Colors, "__format__", _old_color_format)


def patch_all():
    patch_colors()
