<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<!--suppress ALL -->
<script lang="ts">
	import { socket } from '$lib/socket';
	import JoinGame from '$lib/play/join.svelte';
	import type { Answer, Question as QuestionType } from '$lib/quiz_types';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	// import ShowResults from '$lib/play/show_results.svelte';
	import { navbarVisible } from '$lib/stores';
	import ShowEndScreen from '$lib/play/admin/final_results.svelte';
	import KahootResults from '$lib/play/results_kahoot.svelte';
	import { getLocalization } from '$lib/i18n';
	import Cookies from 'js-cookie';
	const { t } = getLocalization();

	// Exports
	export let data;
	let { game_pin } = data;

	// Types
	interface GameMeta {
		started: boolean;
	}

	let game_mode;
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	// Variables init
	let question_index = '';
	let unique = {};
	navbarVisible.set(false);
	let game_pin_valid: boolean;
	let answer_results: Array<Answer>;
	let gameData;
	let solution: QuestionType;
	let username = '';
	let scores = {};
	let gameMeta: GameMeta = {
		started: false
	};

	let question;

	let preventReload = true;

	// Functions
	function restart() {
		unique = {};
	}

	const confirmUnload = () => {
		if (preventReload) {
			event.preventDefault();
			// eslint-disable-next-line @typescript-eslint/ban-ts-comment
			// @ts-ignore
			event.returnValue = '';
		}
	};

	socket.on('time_sync', (data) => {
		socket.emit('echo_time_sync', data);
	});
	socket.on("session_id", (d) => {
		const session_id = d.session_id
	})

	socket.on('connect', async () => {
		console.log('Connected!');
		const cookie_data = Cookies.get('joined_game');
		if (!cookie_data) {
			return;
		}
		const data = JSON.parse(cookie_data);
		socket.emit('rejoin_game', {
			old_sid: data.sid,
			username: data.username,
			game_pin: data.game_pin
		});
		const res = await fetch(`/api/v1/quiz/play/check_captcha/${game_pin}`);
		const json = await res.json();
		game_mode = json.game_mode;
	});

	// Socket-events
	socket.on('joined_game', (data) => {
		gameData = data;
		// eslint-disable-next-line no-undef
		plausible('Joined Game', { props: { game_id: gameData.game_id } });
		Cookies.set('joined_game', JSON.stringify({ sid: socket.id, username, game_pin }), {
			expires: 3600
		});
	});
	socket.on('rejoined_game', (data) => {
		gameData = data;
		if (data.started) {
			gameMeta.started = true;
		}
	});

	socket.on('game_not_found', () => {
		const cookie_data = Cookies.get('joined_game');
		if (cookie_data) {
			Cookies.remove('joined_game');
			window.location.reload();
			return;
		}
		game_pin_valid = false;
	});

	socket.on('set_question_number', (data) => {
		solution = undefined;
		restart();
		question = data.question;
		question_index = data.question_index;
		answer_results = undefined;
	});

	socket.on('start_game', () => {
		gameMeta.started = true;
	});

	socket.on('question_results', (data) => {
		restart();
		answer_results = data;
	});

	socket.on('username_already_exists', () => {
		window.alert('Username already exists!');
	});

	socket.on('kick', () => {
		window.alert('You got kicked');
		preventReload = false;
		game_pin = '';
		username = '';
		Cookies.set('kicked', 'value', { expires: 1 });
		window.location.reload();
	});
	socket.on('final_results', (data) => {
		final_results = data;
		Cookies.remove('joined_game');
	});

	socket.on('solutions', (data) => {
		solution = data;
	});

	let bg_color;
	$: bg_color = gameData ? gameData.background_color : undefined;
	// The rest
</script>

<svelte:window on:beforeunload={confirmUnload} />
<svelte:head>
	<title>ClassQuiz - Play</title>
	<!--	{#if gameData !== undefined && game_mode !== 'kahoot'}
		{#each gameData.questions as question}
			{#if question.image !== undefined}
				<link rel="preload" as="image" href={question.image} />
			{/if}
		{/each}
	{/if}-->
</svelte:head>
<div
	class="min-h-screen min-w-full"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<div>
		{#if !gameMeta.started && gameData === undefined}
			<JoinGame bind:game_pin bind:game_mode bind:username />
		{:else if JSON.stringify(final_results) !== JSON.stringify([null])}
			<ShowEndScreen bind:data={scores} show_final_results={true} bind:username />
		{:else if gameData !== undefined && question_index === ''}
			<ShowTitle
				bind:title={gameData.title}
				bind:description={gameData.description}
				bind:cover_image={gameData.cover_image}
			/>
		{:else if gameMeta.started && gameData !== undefined && question_index !== '' && answer_results === undefined}
			{#key unique}
				<div class="text-black dark:text-black">
					<Question bind:game_mode bind:question bind:question_index bind:solution />
				</div>
			{/key}
		{:else if gameMeta.started && answer_results !== undefined}
			{#if answer_results === null}
				<div class="w-full flex justify-center">
					<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
				</div>
			{:else}
				<div>
					<h2 class="text-center text-3xl mb-8">{$t('words.result', { count: 2 })}</h2>
				</div>
				{#key unique}
					<KahootResults
						bind:username
						bind:question_results={answer_results}
						bind:scores
					/>
				{/key}
			{/if}
		{/if}
	</div>
</div>
