// SPDX-FileCopyrightText: 2026
//
// SPDX-License-Identifier: MPL-2.0

// IDs from the page address are pasted into API paths. Anything that isn't an
// ID (for example "../../storage/download/<file>") would make the page load a
// different API route, so reject it before fetching.
const ID_PATTERN = /^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$/i;

export const is_id = (value: string | null | undefined): value is string =>
	typeof value === 'string' && ID_PATTERN.test(value);
