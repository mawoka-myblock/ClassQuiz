<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';

	import { socket } from '$lib/socket';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores';
	import type { PlayerAnswer, Player } from '$lib/admin.ts';
	import SomeAdminScreen from '$lib/admin.svelte';
	import GameNotStarted from '$lib/play/admin/game_not_started.svelte';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';
	import FinalResults from '$lib/play/admin/final_results.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { page } from '$app/stores';

	navbarVisible.set(false);

	const { t } = getLocalization();

	// let gameData = {
	// 	game_id: 'a7ddb6af-79ab-45e0-b996-6254c1ad9818',
	// 	game_pin: '66190765'
	// };
	export let data;
	let game_mode;
	let { auto_connect, game_token } = data;
	const game_pin = data.game_pin;

	let players: Array<Player> = [];
	let player_scores = {};
	let errorMessage = '';
	let game_started = false;
	let quiz_data: QuizData;
	let control_visible = true;
	//let question_number = '0';
	// let question_results = null;
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let success = false;
	let dataexport_download_a;
	let warnToLeave = true;
	let export_token = undefined;

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
	socket.on("session_id", (d) => {
		const session_id = d.session_id
	})

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

	socket.on('start_game', (_) => {
		game_started = true;
	});

	socket.on('control_visibility', (data) => {
		control_visible = data.visible;
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
		export_token = int_data;

		setTimeout(() => {
			warnToLeave = true;
		}, 200);
	});

	socket.on('results_saved_successfully', (_) => {
		results_saved = true;
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
	const save_quiz = async () => {
		await socket.emit('save_quiz');
	};

	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	let bg_color;
	let bg_image;
	let results_saved = false;
	$: bg_color = quiz_data ? quiz_data.background_color : undefined;
	$: bg_image = quiz_data ? quiz_data.background_image : undefined;
	let show_final_results = false;
	$: show_final_results = JSON.stringify(final_results) !== JSON.stringify([null]);
</script>

<svelte:window on:beforeunload={confirmUnload} />
<svelte:head>
	<title>ClassQuiz - Host</title>
</svelte:head>
<div
	class="min-h-screen min-w-full"
	style="background-repeat: no-repeat;background-size: 100% 100%;background-image: {bg_image
		? `url('${bg_image}')`
		: `unset`}; background-color: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	{#if JSON.stringify(final_results) !== JSON.stringify([null])}
		{#if control_visible}
			<div class="w-screen flex justify-center mt-16">
				<div class="w-fit">
					{#if export_token === undefined}
						<GrayButton on:click={request_answer_export}
							>{$t('admin_page.request_export_results')}</GrayButton
						>
					{:else}
						<GrayButton
							target="_blank"
							href="/api/v1/quiz/export_data/{export_token}?ts={new Date().getTime()}&game_pin={game_pin}"
							>{$t('admin_page.download_export_results')}</GrayButton
						>
					{/if}
				</div>
			</div>
			<div class="w-screen flex justify-center mt-2">
				<div class="w-fit">
					<GrayButton on:click={save_quiz} flex={true} disabled={results_saved}>
						{#if results_saved}
							<svg
								class="w-4 h-4"
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M5 13l4 4L19 7"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						{:else}{$t('admin_page.save_results')}{/if}
					</GrayButton>
				</div>
			</div>
		{/if}
		<FinalResults bind:data={player_scores} bind:show_final_results />
	{/if}
	{#if !success}
		{#if errorMessage !== ''}
			<p class="text-red-700">{errorMessage}</p>
		{/if}
	{:else if !game_started}
		<GameNotStarted
			{game_pin}
			bind:players
			{socket}
			cqc_code={$page.url.searchParams.get('cqc_code')}
		/>
	{:else}
		<SomeAdminScreen
			bind:final_results
			{game_pin}
			bind:game_token
			bind:quiz_data
			bind:game_mode
			bind:bg_color
			bind:player_scores
			bind:control_visible
		/>
	{/if}
</div>
<a
	on:click|preventDefault={request_answer_export}
	href="#"
	target="_blank"
	bind:this={dataexport_download_a}
	download=""
	class="absolute -top-3/4 -left-3/4 opacity-0">Download</a
>
