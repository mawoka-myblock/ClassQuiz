<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { socket } from '$lib/socket';
	import { onDestroy, onMount } from 'svelte';
	import { browser } from '$app/environment';
	import * as Sentry from '@sentry/browser';
	import { alertModal } from '../stores';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let game_pin: string;
	export let game_mode;

	export let username;
	let hcaptchaSitekey = import.meta.env.VITE_HCAPTCHA;

	let hcaptcha = {
		execute: async (_a, _b) => ({ response: '' }), // eslint-disable-line @typescript-eslint/no-unused-vars
		// eslint-disable-next-line @typescript-eslint/no-empty-function
		render: (_a, _b) => {} // eslint-disable-line @typescript-eslint/no-unused-vars
	};
	let hcaptchaWidgetID;

	onMount(() => {
		if (browser) {
			hcaptcha = window.hcaptcha;
			if (hcaptcha.render) {
				hcaptchaWidgetID = hcaptcha.render('hcaptcha', {
					sitekey: hcaptchaSitekey,
					size: 'invisible',
					theme: 'dark'
				});
			}
		}
	});

	onDestroy(() => {
		if (browser) {
			hcaptcha = {
				execute: async () => ({ response: '' }),
				// eslint-disable-next-line @typescript-eslint/no-empty-function
				render: () => {}
			};
		}
	});

	const setUsername = async () => {
		if (username.length <= 3) {
			return;
		}
		let captcha_resp: string;
		const res = await fetch(`/api/v1/quiz/play/check_captcha/${game_pin}`);
		let captcha_enabled;
		const json = await res.json();
		game_mode = json.game_mode;
		if (res.status === 200) {
			captcha_enabled = json.enabled;
		}
		if (res.status === 404) {
			alertModal.set({
				open: true,
				title: 'Game not found',
				body: 'The game pin you entered seems invalid.'
			});
			game_pin = '';
			return;
		}
		if (res.status !== 200) {
			alertModal.set({
				open: true,
				body: `Unknown error with response-code ${res.status}`,
				title: 'Unknown Error'
			});
			return;
		}

		if (captcha_enabled) {
			try {
				const { response } = await hcaptcha.execute(hcaptchaWidgetID, {
					async: true
				});
				captcha_resp = response;
			} catch (e) {
				if (import.meta.env.VITE_SENTRY !== null) {
					Sentry.captureException(e);
				}
				alertModal.set({
					open: true,
					body: "The captcha failed, which is normal, but most of the time it's fixed by reloading!",
					title: 'Captcha failed'
				});
				alertModal.subscribe((data) => {
					if (!data.open) {
						window.location.reload();
					}
				});
			}
		}
		socket.emit('join_game', {
			username: username,
			game_pin: game_pin,
			captcha: captcha_resp
		});
	};
	socket.on('game_not_found', () => {
		game_pin = '';
		alert('Game not found');
	});

	$: game_pin = game_pin.replace(/\D/g, '');
</script>

<svelte:head>
	<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
</svelte:head>

{#if game_pin === '' || game_pin.length <= 7}
	<div class="flex flex-col justify-center align-center w-screen h-screen">
		<form on:submit|preventDefault class="flex-col flex justify-center align-center mx-auto">
			<h1 class="text-lg text-center">{$t('words.game_pin')}</h1>
			<input
				class="border border-gray-400 self-center text-center text-black ring-0 outline-none p-2 rounded-lg focus:shadow-2xl transition-all"
				bind:value={game_pin}
				maxlength="8"
			/>
			<!--				use:tippy={{content: "Please enter the game pin", sticky: true, placement: 'top'}}-->

			<br />
			<button
				class="bg-amber-800 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed mt-2"
				type="submit"
				disabled={game_pin.length <= 7}
			>
				{$t('words.submit')}
			</button>
		</form>
	</div>
{:else}
	<div class="flex flex-col justify-center align-center w-screen h-screen">
		<form
			on:submit|preventDefault={setUsername}
			class="flex-col flex justify-center align-center mx-auto"
		>
			<h1 class="text-lg text-center">{$t('words.username')}</h1>
			<input
				class="border border-gray-400 self-center text-center text-black ring-0 outline-none p-2 rounded-lg focus:shadow-2xl transition-all"
				bind:value={username}
				maxlength="17"
			/>
			<button
				class="bg-amber-800 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded disabled:cursor-not-allowed disabled:opacity-50 mt-2"
				type="submit"
				disabled={username.length <= 3}
			>
				{$t('words.submit')}
			</button>
		</form>
	</div>
{/if}
<div
	id="hcaptcha"
	class="h-captcha"
	data-sitekey={hcaptchaSitekey}
	data-size="invisible"
	data-theme="dark"
/>
