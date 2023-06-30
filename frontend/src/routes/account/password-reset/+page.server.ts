// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

export function load({ url }) {
	const token = url.searchParams.get('token');

	return {
		token
	};
}
