<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { socket } from '$lib/socket';
	import { onDestroy, onMount } from 'svelte';
	import { browser } from '$app/environment';
	import * as Sentry from '@sentry/browser';
	// import { alertModal } from '../stores';
	import { getLocalization } from '$lib/i18n';
	import Cookies from 'js-cookie';
	import BrownButton from '$lib/components/buttons/brown.svelte';

	const { t } = getLocalization();
	export let game_pin: string;
	export let game_mode;

	export let username;
	let custom_field;
	let custom_field_value;
	let captcha_enabled;

	let hcaptchaSitekey = import.meta.env.VITE_HCAPTCHA;

	let hcaptcha = {
		execute: async (_a, _b) => ({ response: '' }), // eslint-disable-line @typescript-eslint/no-unused-vars
		// eslint-disable-next-line @typescript-eslint/no-empty-function
		render: (_a, _b) => {} // eslint-disable-line @typescript-eslint/no-unused-vars
	};
	let hcaptchaWidgetID;

	onMount(() => {
		if (browser) {
			prefetch_username();
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

	const prefetch_username = async () => {
		const res = await fetch('/api/v1/users/me');
		if (res.status !== 200) {
			return;
		}
		const json = await res.json();
		username = json.username;
	};

	const set_game_pin = async () => {
		let process_var;
		try {
			process_var = process;
		} catch {
			process_var = { env: { API_URL: undefined } };
		}

		const res = await fetch(
			`${process_var.env.API_URL ?? ''}/api/v1/quiz/play/check_captcha/${game_pin}`
		);
		const json = await res.json();
		game_mode = json.game_mode;
		if (res.status === 200) {
			captcha_enabled = json.enabled;
			custom_field = json.custom_field;
		}
		if (res.status === 404) {
			/*			alertModal.set({
                open: true,
                title: 'Game not found',
                body: 'The game pin you entered seems invalid.'
            });*/
			if (browser) {
				alert('Game not found');
			}
			game_pin = '';
			return;
		}
		if (res.status !== 200) {
			/*			alertModal.set({
                open: true,
                body: `Unknown error with response-code ${res.status}`,
                title: 'Unknown Error'
            });*/
			alert('Unknown error');
			return;
		}
	};

	$: if (game_pin.length > 5) {
		console.log('Setting game pin');
		set_game_pin();
	}

	const setUsername = async () => {
		if (username.length <= 3) {
			return;
		}
		let captcha_resp: string;
		if (Cookies.get('kicked')) {
			console.log("%cYou're Banned!", 'font-size:6rem');
			return;
		}

		if (captcha_enabled) {
			if (hcaptchaSitekey) {
				try {
					const { response } = await hcaptcha.execute(hcaptchaWidgetID, {
						async: true
					});
					captcha_resp = response;
					socket.emit('join_game', {
						username: username,
						game_pin: game_pin,
						captcha: captcha_resp,
						custom_field: custom_field ? custom_field_value : undefined
					});
				} catch (e) {
					if (import.meta.env.VITE_SENTRY !== null) {
						Sentry.captureException(e);
					}
					/*					alertModal.set({
                        open: true,
                        body: "The captcha failed, which is normal, but most of the time it's fixed by reloading!",
                        title: 'Captcha failed'
                    });*/
					alert('Captcha failed!');
					window.location.reload();
				}
			} else if (import.meta.env.VITE_RECAPTCHA) {
				// eslint-disable-next-line no-undef
				grecaptcha.ready(() => {
					// eslint-disable-next-line no-undef
					grecaptcha
						.execute(import.meta.env.VITE_RECAPTCHA, { action: 'submit' })
						.then(function (token) {
							socket.emit('join_game', {
								username: username,
								game_pin: game_pin,
								captcha: token,
								custom_field: custom_field ? custom_field_value : undefined
							});
						});
				});
			}
		} else {
			socket.emit('join_game', {
				username: username,
				game_pin: game_pin,
				captcha: undefined,
				custom_field: custom_field ? custom_field_value : undefined
			});
		}
	};
	socket.on('game_not_found', () => {
		game_pin = '';
		if (browser) {
			alert('Game not found');
		}
	});

	$: console.log(game_pin, game_pin.length > 6);
	$: game_pin = game_pin.replace(/\D/g, '');
</script>

<svelte:head>
	{#if captcha_enabled && hcaptchaSitekey}
		<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
	{/if}
	{#if import.meta.env.VITE_RECAPTCHA && captcha_enabled}
		<script
			src="https://www.google.com/recaptcha/api.js?render={import.meta.env.VITE_RECAPTCHA}"
		></script>
	{/if}
</svelte:head>

{#if game_pin === '' || game_pin.length < 6}
	<div class="flex flex-col justify-center align-center w-screen h-screen">
		<form on:submit|preventDefault class="flex-col flex justify-center align-center mx-auto">
			<h1 class="text-lg text-center">{$t('words.game_pin')}</h1>
			<input
				class="border border-gray-400 self-center text-center text-black ring-0 outline-none p-2 rounded-lg focus:shadow-2xl transition-all"
				bind:value={game_pin}
				maxlength="6"
				inputmode="numeric"
			/>
			<!--				use:tippy={{content: "Please enter the game pin", sticky: true, placement: 'top'}}-->

			<br />
			<div class="mt-2">
				<BrownButton disabled={game_pin.length < 6}>{$t('words.submit')}</BrownButton>
			</div>
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
			{#if custom_field}
				<h1 class="text-lg text-center">{custom_field}</h1>
				<input
					class="border border-gray-400 self-center text-center text-black ring-0 outline-none p-2 rounded-lg focus:shadow-2xl transition-all"
					bind:value={custom_field_value}
				/>
			{/if}

			<div class="mt-2">
				<BrownButton disabled={username.length <= 3} on:click={setUsername}
					>{$t('words.submit')}</BrownButton
				>
			</div>
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
