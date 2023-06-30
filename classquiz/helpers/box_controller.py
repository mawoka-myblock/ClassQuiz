# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import random


def generate_code(specified_length: int) -> str:
    buttons = [
        "B",
        "b",
        "G",
        "g",
        "Y",
        "y",
        "R",
        "r",
    ]  # Capital stands for long press, lowercase letter for short press
    resulting_code = ""
    for _ in range(specified_length):
        resulting_code += random.choice(buttons)
    return resulting_code
