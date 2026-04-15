"""
Compatibility shim for imghdr — removed from Python 3.13+ stdlib.
Tweepy 4.14.x imports this module internally; this shim restores
the minimal API that tweepy needs so the rest of the project works.
"""

import struct


def what(file, h=None):
    """
    Return a string describing the image type of the data in *file*.
    Returns None if the type cannot be determined.

    Supports: png, jpeg, gif, bmp, webp, tiff, rgb
    """
    if h is None:
        if isinstance(file, str):
            with open(file, "rb") as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)

    tests = [
        _test_png,
        _test_jpeg,
        _test_gif,
        _test_bmp,
        _test_webp,
        _test_tiff,
        _test_rgb,
    ]
    for test in tests:
        result = test(h)
        if result:
            return result
    return None


def _test_png(h):
    if h[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"


def _test_jpeg(h):
    if h[:2] == b"\xff\xd8":
        return "jpeg"


def _test_gif(h):
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"


def _test_bmp(h):
    if h[:2] == b"BM":
        return "bmp"


def _test_webp(h):
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        return "webp"


def _test_tiff(h):
    if h[:2] in (b"MM", b"II"):
        return "tiff"


def _test_rgb(h):
    if h[:2] == b"\x01\xda":
        return "rgb"
