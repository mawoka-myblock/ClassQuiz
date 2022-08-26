/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

import { alertModal } from '$lib/stores';
import { captcha_enabled } from '$lib/config';

export const start_game = async (id: string) => {
	let res;
	if (captcha_enabled && window.confirm('Do you want to enable the captcha for players?')) {
		res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=True`, {
			method: 'POST'
		});
	} else {
		res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=False`, {
			method: 'POST'
		});
	}

	if (res.status !== 200) {
		alertModal.set({
			open: true,
			title: 'Start failed',
			body: `Failed to start game, ${await res.text()}`
		});
		alertModal.subscribe((_) => {
			window.location.assign('/account/login?returnTo=/dashboard');
		});
	}
	const data = await res.json();
	// eslint-disable-next-line no-undef
	plausible('Started Game', { props: { quiz_id: id } });
	window.location.assign(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
};
