// SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

(function (process) {
  process.env = process.env || {};

  process['env']['TEST_VARIABLE'] = '${TEST_VARIABLE}';
})(this);