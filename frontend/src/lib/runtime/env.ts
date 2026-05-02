// SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

export const runtimeEnvVarWrapper = {
    get: function (name) {
        try {
            return window.env[name];
        }
        catch (e) {
            return process.env[name];
        }
    }
};