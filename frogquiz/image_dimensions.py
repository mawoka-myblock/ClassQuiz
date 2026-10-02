# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

"""Pixel dimensions read from an image header, without decoding the image.

The point is never to allocate an attacker's raster. A 20000x20000 PNG of one solid
colour is under 400KiB on disk but ~1.6GB as a bitmap, so a byte cap does not bound what
a browser is asked to render -- and the browsers are the clients here, on phones. This
reads the handful of header bytes each format states its size in, and nothing else.

Verified field-by-field against Pillow's own decode for PNG, GIF, baseline and progressive
JPEG, and all three WebP layouts (VP8, VP8L, VP8X); see tests/test_image_dimensions.py.
"""

import struct

# How many header bytes to read. JPEG puts the frame header after a variable run of
# segments (EXIF, ICC profiles), so a few bytes is not enough; 64KiB clears any real
# image and is cheap. The caller passes at most this many bytes.
HEADER_BYTES = 65536


def image_dimensions(head: bytes) -> tuple[int, int] | None:
    """(width, height), or None if `head` is not a recognised image or is truncated."""
    # PNG: signature then IHDR, which is always the first chunk; dimensions big-endian.
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        if len(head) >= 24 and head[12:16] == b"IHDR":
            return struct.unpack(">II", head[16:24])
        return None

    # GIF: 'GIF87a'/'GIF89a' then the logical-screen width/height, little-endian.
    if head[:6] in (b"GIF87a", b"GIF89a"):
        if len(head) >= 10:
            return struct.unpack("<HH", head[6:10])
        return None

    # WebP: 'RIFF' .... 'WEBP' then one of three chunk layouts.
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        fmt = head[12:16]
        if fmt == b"VP8 " and len(head) >= 30:  # lossy
            w = struct.unpack("<H", head[26:28])[0] & 0x3FFF
            h = struct.unpack("<H", head[28:30])[0] & 0x3FFF
            return w, h
        if fmt == b"VP8L" and len(head) >= 25:  # lossless
            bits = head[21] | (head[22] << 8) | (head[23] << 16) | (head[24] << 24)
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if fmt == b"VP8X" and len(head) >= 30:  # extended (animation, alpha)
            w = 1 + (head[24] | (head[25] << 8) | (head[26] << 16))
            h = 1 + (head[27] | (head[28] << 8) | (head[29] << 16))
            return w, h
        return None

    # JPEG: walk the marker segments to the Start-Of-Frame. The dimensions are not at a
    # fixed offset -- EXIF and ICC segments come first and vary in length -- so this reads
    # each segment's length and skips it, decoding nothing.
    if head[:2] == b"\xff\xd8":
        i = 2
        n = len(head)
        while i + 9 < n:
            if head[i] != 0xFF:
                i += 1
                continue
            marker = head[i + 1]
            # SOF0..SOF15 carry the frame size; SOF4/8/12 (DHT/JPG/DAC) do not.
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h = struct.unpack(">H", head[i + 5 : i + 7])[0]
                w = struct.unpack(">H", head[i + 7 : i + 9])[0]
                return w, h
            # Standalone markers (SOI/EOI/RSTn) have no length field.
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = struct.unpack(">H", head[i + 2 : i + 4])[0]
            i += 2 + seg_len
        return None

    return None
