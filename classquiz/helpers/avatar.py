# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import py_avataaars_no_png as pa
from random import choice
import gzip


def _gen_avatar() -> str:
    mouth_type = pa.MouthType
    avatar = pa.PyAvataaar(
        style=pa.AvatarStyle.TRANSPARENT,
        skin_color=choice(list(pa.SkinColor)),
        hair_color=choice(list(pa.HairColor)),
        facial_hair_type=choice(list(pa.FacialHairType)),
        facial_hair_color=choice(list(pa.HairColor)),
        top_type=choice(list(pa.TopType)),
        hat_color=choice(list(pa.Color)),
        mouth_type=choice([mouth_type.DEFAULT, mouth_type.SMILE, mouth_type.TONGUE, mouth_type.TWINKLE]),
        eye_type=pa.EyesType.DEFAULT,  # choice(list(pa.EyesType))
        eyebrow_type=choice(list(pa.EyebrowType)),
        nose_type=choice(list(pa.NoseType)),
        accessories_type=choice(list(pa.AccessoriesType)),
        clothe_type=choice(list(pa.ClotheType)),
        clothe_color=choice(list(pa.Color)),
        clothe_graphic_type=choice(list(pa.ClotheGraphicType)),
    )
    return avatar.render_svg()


def gzipped_user_avatar() -> bytes:
    return gzip.compress(str.encode(_gen_avatar()))


def str_user_avatar() -> str:
    return _gen_avatar()
