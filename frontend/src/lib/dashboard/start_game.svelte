<!--
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->
<script lang="ts">
	import { alertModal } from '$lib/stores';
	import { captcha_enabled } from '$lib/config';
	import StartGameBackground from './start_game_background.svg';
	import { fade } from 'svelte/transition';

	export let quiz_id;
	let captcha_selected = false;
	let selected_game_mode = 'normal';

	const start_game = async (id: string) => {
		let res;
		if (captcha_enabled && captcha_selected) {
			res = await fetch(
				`/api/v1/quiz/start/${id}?captcha_enabled=True&game_mode=${selected_game_mode}`,
				{
					method: 'POST'
				}
			);
		} else {
			res = await fetch(
				`/api/v1/quiz/start/${id}?captcha_enabled=False&game_mode=${selected_game_mode}`,
				{
					method: 'POST'
				}
			);
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
		} else {
			const data = await res.json();
			// eslint-disable-next-line no-undef
			plausible('Started Game', { props: { quiz_id: id } });
			window.location.assign(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
		}
	};
</script>

<div
	class="fixed top-0 left-0 flex justify-center w-screen h-screen bg-black bg-opacity-60 z-50 text-black"
	transition:fade={{ duration: 100 }}
>
	<div
		class="w-5/6 h-5/6 bg-black m-auto rounded-lg shadow-lg p-4 flex flex-col"
		style="background-image: url({StartGameBackground}); background-color: #DFDBE5;"
	>
		<div class="flex justify-center w-full">
			<label
				for="large-toggle"
				class="inline-flex relative items-center cursor-pointer"
				class:pointer-events-none={!captcha_enabled}
				class:opacity-50={!captcha_enabled}
			>
				<input
					type="checkbox"
					bind:checked={captcha_selected}
					id="large-toggle"
					class="sr-only peer"
				/>
				<span
					class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
				/>
				<span class="ml-3 text-sm font-medium text-gray-900"
					>Captcha {captcha_selected ? 'enabled' : 'disabled'}</span
				>
			</label>
		</div>

		<div class="grid grid-cols-2 gap-8 my-auto">
			<div
				class="rounded-lg bg-white shadow-lg cursor-pointer transition-all p-2"
				class:opacity-50={selected_game_mode !== 'normal'}
				on:click={() => {
					selected_game_mode = 'normal';
				}}
			>
				<h2 class="text-center text-2xl">Normal</h2>
				<p>
					Questions, images and answers will be shown on both admins screen and on the
					screen of the players
				</p>
			</div>
			<div
				class="rounded-lg bg-white shadow-lg cursor-pointer transition-all p-2"
				class:opacity-50={selected_game_mode !== 'kahoot'}
				on:click={() => {
					selected_game_mode = 'kahoot';
				}}
			>
				<h2 class="text-center text-2xl">Kahoot!-Like [EARLY BETA]</h2>
				<p>
					Question and answer will only be shown on admins screen, like Kahoot!. The
					players will only have colored buttons with symbols matching these on the screen
					of the admin.
				</p>
			</div>
		</div>

		<button
			class="mt-auto mx-auto bg-green-500 p-4 rounded-lg shadow-lg"
			on:click={() => {
				start_game(quiz_id);
			}}
		>
			START GAME
		</button>
	</div>
</div>
