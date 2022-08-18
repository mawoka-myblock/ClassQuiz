<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script context="module" lang="ts">
	throw new Error(
		'@migration task: Check code was safely removed (https://github.com/sveltejs/kit/discussions/5774#discussioncomment-3292722)'
	);

	// import { signedIn } from '$lib/stores';

	// export async function load({ url, session }) {
	// 	if (session.authenticated) {
	// 		signedIn.set(true);
	// 	}
	// 	const token = url.searchParams.get('pin');
	// 	return {
	// 		props: {
	// 			game_pin: token === null ? '' : token
	// 		}
	// 	};
	// }
</script>

<script lang="ts">
	throw new Error(
		'@migration task: Add data prop (https://github.com/sveltejs/kit/discussions/5774#discussioncomment-3292707)'
	);

	import { socket } from '$lib/socket';
	import JoinGame from '$lib/play/join.svelte';
	import type { Answer, QuizData } from '$lib/quiz_types';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import ShowResults from '$lib/play/show_results.svelte';
	import { navbarVisible } from '$lib/stores';
	import ShowEndScreen from '$lib/play/end.svelte';
	import { QuizQuestionType } from '$lib/quiz_types';

	// Exports
	export let game_pin: string;

	// Types
	interface GameMeta {
		started: boolean;
	}

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
	let gameData: QuizData;
	let gameMeta: GameMeta = {
		started: false
	};

	// Functions
	function restart() {
		unique = {};
	}

	const confirmUnload = () => {
		event.preventDefault();
		event.returnValue = '';
	};

	// Socket-events
	socket.on('joined_game', (data) => {
		console.log('joined_game', data);
		let temp_data = JSON.parse(data);
		for (let i = 0; i < temp_data.questions.length; i++) {
			let question = temp_data.questions[i];
			if (question.type === undefined) {
				temp_data.questions[i].type = QuizQuestionType.ABCD;
			} else {
				temp_data.questions[i].type = QuizQuestionType[question.type];
			}
		}
		gameData = temp_data;
		// eslint-disable-next-line no-undef
		plausible('Joined Game', { props: { quiz_id: gameData.quiz_id } });
	});

	socket.on('game_not_found', () => {
		game_pin_valid = false;
	});

	socket.on('set_question_number', (data) => {
		restart();
		answer_results = undefined;
		question_index = data;
	});

	socket.on('start_game', () => {
		gameMeta.started = true;
	});

	socket.on('question_results', (data) => {
		restart();
		answer_results = JSON.parse(data);
	});

	socket.on('final_results', (data) => {
		final_results = data;
	});
	// The rest
</script>

<svelte:window on:beforeunload={confirmUnload} />
<svelte:head>
	<title>ClassQuiz - Play</title>
	{#if gameData !== undefined}
		{#each gameData.questions as question}
			{#if question.image !== undefined}
				<link rel="preload" as="image" href={question.image} />
			{/if}
		{/each}
	{/if}
</svelte:head>
<div>
	{#if !gameMeta.started && gameData === undefined}
		<JoinGame {game_pin} />
	{:else if JSON.stringify(final_results) !== JSON.stringify([null])}
		<ShowEndScreen bind:final_results bind:quiz_data={gameData} />
	{:else if gameData !== undefined && question_index === ''}
		<ShowTitle bind:title={gameData.title} bind:description={gameData.description} />
	{:else if gameMeta.started && gameData !== undefined && question_index !== '' && answer_results === undefined}
		{#key unique}
			<Question
				bind:question={gameData.questions[parseInt(question_index)]}
				bind:question_index
			/>
		{/key}
	{:else if gameMeta.started && answer_results !== undefined}
		{#key unique}
			<ShowResults
				bind:results={answer_results}
				bind:game_data={gameData}
				bind:question_index
			/>
		{/key}
	{/if}
</div>
