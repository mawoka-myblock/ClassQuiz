<script lang="ts">
	import { socket } from '$lib/socket';
	import { onDestroy, onMount } from 'svelte';
	import { browser } from '$app/env';
	import * as Sentry from '@sentry/browser';

	export let game_pin: string;

	let username = '';
	let hcaptchaSitekey = import.meta.env.VITE_HCAPTCHA;

	let hcaptcha = {
		execute: async (_a, _b) => ({ response: '' }),
		render: (_a, _b) => {}
	};
	let hcaptchaWidgetID: any;

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
				render: () => {}
			};
		}
	});

	const setUsername = async () => {
		if (username.length <= 3) {
			return;
		}
		let captcha_resp: string;
		try {
			const { response } = await hcaptcha.execute(hcaptchaWidgetID, {
				async: true
			});
			captcha_resp = response;
			captcha_resp = '';
		} catch (e) {
			if (import.meta.env.VITE_SENTRY !== null) {
				Sentry.captureException(e);
			}
			alert('Captcha failed, reloading the page probably helps!');
			window.location.reload();
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
</script>

<svelte:head>
	<script src="https://js.hcaptcha.com/1/api.js?render=explicit" async defer></script>
</svelte:head>

{#if game_pin === '' || game_pin.length <= 7}
	<div class="flex flex-col justify-center align-center w-screen h-screen">
		<form
			on:submit|preventDefault={() => {}}
			class="flex-col flex justify-center align-center mx-auto"
		>
			<h1 class="text-lg text-center">Game Pin</h1>
			<input
				class="border border-amber-800 self-center text-center text-black"
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
				Submit
			</button>
		</form>
	</div>
{:else}
	<div class="flex flex-col justify-center align-center w-screen h-screen">
		<form
			on:submit|preventDefault={setUsername}
			class="flex-col flex justify-center align-center mx-auto"
		>
			<h1 class="text-lg text-center">Username</h1>
			<input class="border border-amber-800 text-black text-center" bind:value={username} />
			<button
				class="bg-amber-800 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded disabled:cursor-not-allowed disabled:opacity-50 mt-2"
				type="submit"
				disabled={username.length <= 3}
			>
				Submit
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
