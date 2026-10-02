# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""The header-only dimension parser, checked field-by-field against Pillow's own decode.

This is the parser that stops a decompression bomb -- a tiny file that is enormous in
pixels -- from reaching a browser. It reads header bytes and never decodes, so the one
risk is that it reads the wrong bytes; every case here cross-checks it against a real
encoder.
"""

import io

import pytest

from frogquiz.image_dimensions import image_dimensions


def _encode(fmt: str, size: tuple[int, int], **kw) -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(buf, fmt, **kw)
    return buf.getvalue()


@pytest.mark.parametrize(
    "fmt,size,kw",
    [
        ("PNG", (1, 1), {}),
        ("PNG", (1234, 567), {}),
        ("GIF", (640, 480), {}),
        ("JPEG", (800, 600), {}),
        ("JPEG", (1234, 567), {"progressive": True}),
        ("JPEG", (5000, 5000), {}),
        ("WEBP", (300, 200), {"lossless": True}),
        ("WEBP", (640, 481), {"quality": 80}),
        ("WEBP", (321, 123), {"lossless": True}),
    ],
)
def test_matches_a_real_encoder(fmt, size, kw):
    data = _encode(fmt, size, **kw)
    assert image_dimensions(data[:65536]) == size


def test_a_bomb_is_measured_without_being_decoded():
    # 20000x20000 greyscale of one colour: ~380KiB on disk, ~1.6GB as a bitmap. The parser
    # must report its real size from the header alone -- decoding it here would be the very
    # allocation the parser exists to prevent.
    import struct
    import zlib

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    w = h = 20000
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    co = zlib.compressobj(9)
    row = b"\x00" + b"\x00" * w
    body = b"".join(co.compress(row) for _ in range(h)) + co.flush()
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", body) + chunk(b"IEND", b"")
    assert len(png) < 5_000_000  # under the byte cap, which is the whole problem
    assert image_dimensions(png[:1024]) == (20000, 20000)


def test_non_image_and_truncated_bytes_are_not_mistaken_for_a_size():
    assert image_dimensions(b"this is not an image at all, just prose") is None
    assert image_dimensions(b"") is None
    # A PNG signature with the IHDR cut off: unreadable, so None rather than a guess.
    assert image_dimensions(b"\x89PNG\r\n\x1a\n\x00\x00") is None


def test_svg_is_not_a_recognised_raster():
    # SVG is never accepted for upload (it is a script vector), but if one reached here it
    # must not be mistaken for a sized raster -- it has no pixel dimensions to bomb with.
    assert image_dimensions(b'<svg width="10" height="10"></svg>') is None
