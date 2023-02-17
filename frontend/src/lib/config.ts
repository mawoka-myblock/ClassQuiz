/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

export const google_auth_enabled = import.meta.env.VITE_GOOGLE_AUTH_ENABLED === 'true';
export const github_auth_enabled = import.meta.env.VITE_GITHUB_AUTH_ENABLED === 'true';
export const captcha_enabled = import.meta.env.VITE_CAPTCHA_ENABLED === 'true';
export const custom_oauth_name = import.meta.env.VITE_CUSTOM_OAUTH_NAME;
