<script context="module" lang="ts">
	export async function load({ url }) {
		const token = url.searchParams.get('pin');
		return {
			props: {
				game_pin: token === null ? '' : token
			}
		};
	}
</script>

<script lang="ts">
	import { socket } from '$lib/socket';
	import JoinGame from '$lib/play/join.svelte';
	import type { Answer, QuizData } from '../app';
	import ShowTitle from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import ShowResults from '$lib/play/show_results.svelte';
	// Exports
	export let game_pin: string;

	// Types
	interface GameMeta {
		started: boolean;
	}

	// Variables init
	let question_index = '';
	let unique = {};
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

	// Socket-events
	socket.on('joined_game', (data) => {
		console.log('joined_game', data);
		gameData = JSON.parse(data);
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
	// The rest

	$: console.log(gameMeta.started, gameData !== undefined, question_index !== '');
</script>

<div>
	{#if !gameMeta.started && gameData === undefined}
		<JoinGame {game_pin} />
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
