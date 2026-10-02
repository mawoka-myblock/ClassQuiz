<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { socket } from '$lib/socket';
	import { onDestroy, onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { getLocalization } from '$lib/i18n';
	import Cookies from 'js-cookie';
	import Wordmark from '$lib/components/Wordmark.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { hcaptcha_site_key, recaptcha_key } from '$lib/config';

	const { t } = getLocalization();

	interface Props {
		game_pin: string;
		game_mode: any;
		username: any;
		/** Bindable so the page can arrive here with a reason, e.g. after a kick. */
		error_message?: string;
	}

	let {
		game_pin = $bindable(),
		game_mode = $bindable(),
		username = $bindable(),
		error_message = $bindable('')
	}: Props = $props();
	let custom_field = $state();
	// '' rather than undefined: this is bound to a text input, and an undefined
	// value there makes Svelte render the box with the literal string "undefined"
	// the first time a keystroke is undone, and sends undefined on submit even
	// though the server distinguishes "" (not supplied) from a real answer.
	let custom_field_value = $state('');
	let captcha_enabled = $state();
	// error_message is shown under the form instead of a browser alert(), which on a
	// phone is a system dialog that reads like the page has crashed.

	// The server takes any non-blank nickname. The old minimum of four rejected "Ana"
	// and "Rui" with a greyed-out button and no word of why.
	const MIN_NICKNAME = 2;

	// Mirrors MAX_CUSTOM_FIELD_LENGTH in frogquiz/socket_server/models.py. Without
	// it a player could type past the server's cap and only find out by having the
	// join rejected, with nothing shown on this screen to say why.
	const MAX_CUSTOM_FIELD_LENGTH = 200;

	let hcaptchaSitekey = hcaptcha_site_key;

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
			error_message = $t('play_page.game_not_found');
			game_pin = '';
			return;
		}
		if (res.status !== 200) {
			error_message = $t('play_page.unknown_error');
			return;
		}
		error_message = '';
	};

	$effect(() => {
		if (game_pin.length > 5) {
			set_game_pin();
		}
	});

	const setUsername = async (e: Event) => {
		e.preventDefault();
		// Trim before both the check and the send. Untrimmed, four spaces passed
		// as a nickname and the server -- which does bound and trim it -- would
		// then reject a join the form had accepted, with nothing shown here.
		username = username.trim();
		if (username.length < MIN_NICKNAME) {
			return;
		}
		let captcha_resp: string;
		// Holds the PIN of the game the host removed this player from. It used to be a
		// bare flag that silently refused every game for a day, with only a console
		// message to say why.
		if (Cookies.get('kicked') === game_pin) {
			error_message = $t('play_page.kicked');
			return;
		}
		error_message = '';

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
					console.error(e);
					/*					alertModal.set({
                        open: true,
                        body: "The captcha failed, which is normal, but most of the time it's fixed by reloading!",
                        title: 'Captcha failed'
                    });*/
					alert('Captcha failed!');
					window.location.reload();
				}
			} else if (recaptcha_key) {
				// eslint-disable-next-line no-undef
				grecaptcha.ready(() => {
					// eslint-disable-next-line no-undef
					grecaptcha.execute(recaptcha_key, { action: 'submit' }).then(function (token) {
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
		error_message = $t('play_page.game_not_found');
	});
	socket.on('game_already_started', () => {
		game_pin = '';
		error_message = $t('play_page.game_already_started');
	});
	socket.on('username_already_exists', () => {
		error_message = $t('play_page.username_taken');
	});
	$effect(() => {
		const cleaned = game_pin.replace(/\D/g, '');
		if (game_pin.replace(/\D/g, '') === game_pin) {
			return;
		}
		game_pin = cleaned;
	});
</script>

<svelte:head>
	{#if captcha_enabled && hcaptchaSitekey}
		<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
	{/if}
	{#if recaptcha_key && captcha_enabled}
		<script src="https://www.google.com/recaptcha/api.js?render={recaptcha_key}"></script>
	{/if}
</svelte:head>

<!-- fq-stage, not min-h-screen: 100vh counts browser chrome that is not there on a
     phone, which is where every player is, and pushed the submit button below the
     fold.
     This screen is the first thing every player sees, and it was a floating label, an
     unlabelled box and a grey Submit on an empty page -- while the landing page next
     door already did the same job in a card. Same card here: the mark, so you can see
     you are in the right place, one field, and one full-width primary action. -->
<div class="fq-stage">
	<div class="flex w-full max-w-sm flex-col items-center gap-6">
		<Wordmark size={44} />

		{#if game_pin === '' || game_pin.length < 6}
			<!-- No submit handler of its own: the sixth digit advances it. Without this,
			     Enter did a native submit and reloaded the page. -->
			<form
				class="border-border/70 bg-card w-full rounded-xl border p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04),0_16px_40px_-24px_rgba(0,0,0,0.25)]"
				onsubmit={(e) => e.preventDefault()}
			>
				<Label for="game-pin" class="text-sm font-medium">{$t('words.game_pin')}</Label>
				<p class="text-muted-foreground mt-1.5 text-sm">
					{$t('index_page.join_prompt')}
				</p>
				<Input
					id="game-pin"
					bind:value={game_pin}
					maxlength={6}
					inputmode="numeric"
					pattern="[0-9]*"
					autocomplete="one-time-code"
					class="mt-4 h-12 text-center font-mono text-xl tracking-[0.35em]"
					autofocus
				/>
				{#if error_message}
					<p class="text-destructive mt-3 text-sm text-balance" role="alert">
						{error_message}
					</p>
				{/if}
				<Button
					type="submit"
					size="lg"
					class="mt-4 h-12 w-full disabled:bg-muted disabled:text-muted-foreground disabled:opacity-100"
					disabled={game_pin.length < 6}
				>
					{$t('words.submit')}
				</Button>
			</form>
		{:else}
			<form
				onsubmit={setUsername}
				class="border-border/70 bg-card w-full rounded-xl border p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04),0_16px_40px_-24px_rgba(0,0,0,0.25)]"
			>
				<Label for="join-username" class="text-sm font-medium">{$t('words.username')}</Label
				>
				<p id="join-username-hint" class="text-muted-foreground mt-1.5 text-sm">
					{$t('play_page.nickname_hint', { count: MIN_NICKNAME })}
				</p>
				<!-- autocomplete="nickname", not the browser default of guessing: with no
				     token at all Chrome and Safari read this as an account field and
				     offered the player's saved email address for what is a game nickname
				     shown to the whole room. -->
				<Input
					id="join-username"
					bind:value={username}
					maxlength={17}
					autocomplete="nickname"
					aria-describedby="join-username-hint"
					class="mt-4 h-12 text-center text-lg"
				/>

				{#if custom_field}
					<!-- The label text is whatever the host typed when starting the game, so it
					     is tied to the input with for/id rather than left as a heading that
					     happens to sit above it. -->
					<Label
						for="join-custom-field"
						class="mt-5 block text-sm font-medium text-balance"
					>
						{custom_field}
					</Label>
					<Input
						id="join-custom-field"
						bind:value={custom_field_value}
						maxlength={MAX_CUSTOM_FIELD_LENGTH}
						autocomplete="off"
						class="mt-2 h-12 text-center"
					/>
				{/if}

				{#if error_message}
					<p class="text-destructive mt-3 text-sm text-balance" role="alert">
						{error_message}
					</p>
				{/if}
				<Button
					type="submit"
					size="lg"
					class="mt-4 h-12 w-full disabled:bg-muted disabled:text-muted-foreground disabled:opacity-100"
					disabled={username.trim().length < MIN_NICKNAME}
					onclick={setUsername}
				>
					{$t('words.submit')}
				</Button>
			</form>
		{/if}
	</div>
</div>
<div
	id="hcaptcha"
	class="h-captcha"
	data-sitekey={hcaptchaSitekey}
	data-size="invisible"
	data-theme="dark"
></div>
