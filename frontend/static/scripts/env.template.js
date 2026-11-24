// SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

// This function is called in frontend
// Each variable is replaced by envsubst in the Dockerfile, so that they can be set at runtime
// The syntax should be ```window.env.VARIABLE_NAME = '${VARIABLE_NAME}';```
(function (window) {
	window.env = window.env || {};

	window.env.TEST_VARIABLE = '${TEST_VARIABLE}';
})(this);
