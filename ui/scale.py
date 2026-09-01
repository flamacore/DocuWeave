"""UI scale factor.

Qt5 drops icon pixmaps on stylesheet-styled widgets at a device pixel ratio
below 1, so the UI is scaled by multiplying the pixel sizes the widgets ask
for rather than by setting QT_SCALE_FACTOR. Windows display scaling still
applies on top of this: Qt reports logical screen geometry, so a 4K screen at
150% is seen here as 1440p and is not scaled twice.

Scale 1.0 means the sizes hardcoded in the widgets, unchanged.

Resolution order: DOCUWEAVE_SCALE env var, then the saved View > UI Scale
setting, then automatic detection from the screen height.
"""
import os
import re

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

MIN_SCALE = 0.6
MAX_SCALE = 2.0

SETTINGS_KEY = "ui_scale"

# Logical screen height -> scale. Larger screens can carry a larger UI.
_AUTO_STEPS = ((800, 0.65), (1000, 0.70), (1200, 0.75), (1600, 0.80))
_AUTO_ABOVE_STEPS = 1.00

# Choices offered by the View > UI Scale menu.
MENU_CHOICES = (None, 0.70, 0.80, 0.90, 1.00, 1.25, 1.50)

_PIXEL_VALUE = re.compile(r"(\d+)px")

_scale = None


def settings():
    return QSettings("DocuWeave", "DocuWeave")


def auto_scale(logical_height):
    """Scale to use on a screen this tall, in logical pixels."""
    for max_height, scale in _AUTO_STEPS:
        if logical_height <= max_height:
            return scale
    return _AUTO_ABOVE_STEPS


def _saved_scale():
    """Scale saved by the UI Scale menu, or None for automatic."""
    raw = settings().value(SETTINGS_KEY, "auto")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def save_scale(scale):
    """Persist a menu choice. None means automatic detection."""
    settings().setValue(SETTINGS_KEY, "auto" if scale is None else str(scale))


def _screen_height():
    screen = QApplication.primaryScreen()
    return screen.availableGeometry().height() if screen else 1080


def _resolve():
    raw = os.environ.get("DOCUWEAVE_SCALE")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass  # unusable value: fall through to the saved setting
    saved = _saved_scale()
    if saved is not None:
        return saved
    return auto_scale(_screen_height())


def ui_scale():
    """The scale in use this session, resolved once."""
    global _scale
    if _scale is None:
        _scale = max(MIN_SCALE, min(MAX_SCALE, _resolve()))
    return _scale


def reset():
    """Forget the resolved scale. For tests and after a settings change."""
    global _scale
    _scale = None


def px(value):
    """A scaled pixel size. Never rounds down to nothing."""
    return max(1, int(round(value * ui_scale())))


def scaled_css(css):
    """Stylesheet with every `Npx` length scaled."""
    if ui_scale() == 1.0:
        return css
    return _PIXEL_VALUE.sub(lambda match: f"{px(int(match.group(1)))}px", css)
