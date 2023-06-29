#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
