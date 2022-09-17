<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';

	import { socket } from '$lib/socket';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores';
	import type { PlayerAnswer, Player } from '$lib/admin.ts';
	import SomeAdminScreen from '$lib/admin.svelte';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';

	navbarVisible.set(false);

	const { t } = getLocalization();

	// let gameData = {
	// 	game_id: 'a7ddb6af-79ab-45e0-b996-6254c1ad9818',
	// 	game_pin: '66190765'
	// };
	export let data;
	let game_mode;
	let { game_pin, auto_connect, game_token } = data;

	let players: Array<Player> = [];
	let errorMessage = '';
	let game_started = false;
	let quiz_data: QuizData;
	//let question_number = '0';
	// let question_results = null;
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let success = false;
	let dataexport_download_a;
	let warnToLeave = true;

	const connect = async () => {
		socket.emit('register_as_admin', {
			game_pin: game_pin,
			game_id: game_token
		});
		const res = await fetch(`/api/v1/quiz/play/check_captcha/${game_pin}`);
		const json = await res.json();
		game_mode = json.game_mode;
	};
	onMount(() => {
		if (auto_connect) {
			connect();
		}
	});

	socket.on('registered_as_admin', (data) => {
		quiz_data = JSON.parse(data['game']);
		console.log(quiz_data);
		success = true;
	});
	socket.on('player_joined', (int_data) => {
		players = [...players, int_data];
	});
	socket.on('already_registered_as_admin', () => {
		// eslint-disable-next-line @typescript-eslint/ban-ts-comment
		// @ts-ignore
		errorMessage = $t('admin_page.already_registered_as_admin');
	});

	/*	socket.on('question_results', (int_data) => {
		try {
			int_data = JSON.parse(int_data);
		} catch (e) {
			console.error('Failed to parse question results');
			return;
		}
		question_results = int_data;
	});*/
	socket.on('export_token', (int_data) => {
		warnToLeave = false;
		dataexport_download_a.href = `/api/v1/quiz/export_data/${int_data}?ts=${new Date().getTime()}&game_pin=${game_pin}`;
		dataexport_download_a.click();
		warnToLeave = true;
	});

	const confirmUnload = () => {
		if (warnToLeave) {
			event.preventDefault();
			// eslint-disable-next-line @typescript-eslint/ban-ts-comment
			// @ts-ignore
			event.returnValue = '';
		}
	};

	const request_answer_export = async () => {
		await socket.emit('get_export_token');
	};

	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}
</script>

<svelte:window on:beforeunload={confirmUnload} />
<svelte:head>
	<title>ClassQuiz - Host</title>
</svelte:head>
{#if JSON.stringify(final_results) !== JSON.stringify([null])}
	<div class="w-screen flex justify-center mt-8">
		<button
			on:click={request_answer_export}
			class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
			>{$t('admin_page.export_results')}</button
		>
	</div>
	{#await import('$lib/play/end.svelte') then c}
		<svelte:component this={c.default} bind:final_results bind:quiz_data />
	{/await}
{/if}
{#if !success}
	<input placeholder="game id" bind:value={game_token} />
	<input placeholder="game pin" bind:value={game_pin} />
	<button on:click={connect}>{$t('words.connect')}!</button>
	{#if errorMessage !== ''}
		<p class="text-red-700">{errorMessage}</p>
	{/if}
{:else if !game_started}
	<img
		alt="QR code to join the game"
		src="/api/v1/utils/qr/{quiz_data.game_pin}?dark_mode={darkMode}"
		class="block mx-auto w-1/6"
	/>
	<p class="text-3xl text-center ">{$t('words.pin')}: {quiz_data.game_pin}</p>
	<div class="flex justify-center w-full mt-4">
		<ul class="list-disc pl-8">
			{#if players.length > 0}
				{#each players as player}
					<li>
						<span>{player.username}</span>
						<!--					<button>{$t('words.kick')}</button>-->
					</li>
				{/each}
			{/if}
		</ul>
	</div>
	{#if players.length > 0}
		<div class="flex justify-center w-full mt-4">
			<button
				class="ml-4 px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
				id="startGame"
				on:click={() => {
					socket.emit('start_game', '');
					game_started = true;
				}}
				>{$t('admin_page.start_game')}
			</button>
		</div>
	{/if}
{:else}
	<SomeAdminScreen
		bind:final_results
		bind:game_pin
		bind:game_token
		bind:quiz_data
		bind:game_mode
	/>
{/if}

<a
	on:click|preventDefault={request_answer_export}
	href="#"
	bind:this={dataexport_download_a}
	class="absolute -top-3/4 -left-3/4 opacity-0">Download</a
>
