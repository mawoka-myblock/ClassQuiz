// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

// Not prerendered while hidden: a prerendered page is served as a static file and
// never reaches the DISABLED_ROUTES guard in hooks.server.ts, and a guarded one would
// 404 during the build. Set back to true when this page is un-hidden.
export const prerender = false;
