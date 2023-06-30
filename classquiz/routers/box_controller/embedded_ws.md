<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

## Basic Request

Every request is a json-object: `{"type": "SOME_TYPE", "data": "ANY_DATA"}`

### Types

#### e (Error)

- [ ] Client
- [x] Server

Pretty self-explanatory.

Value is a CamelCase errorcode.
Codes:

- `ValidationError`
- `BadId`

#### bp (ButtonPress)

- [x] Client
- [ ] Server

Sends a button-press to the server, where `data` is either `b`, `g`, `y` or `r`. Capital letters indicate a long-press.
