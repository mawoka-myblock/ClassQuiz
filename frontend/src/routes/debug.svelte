<script lang="ts">
	import type { QuizData } from '../app';
	import Title from '$lib/play/title.svelte';
	import Question from '$lib/play/question.svelte';
	import { socket } from '$lib/socket';

	interface GameMeta {
		started: boolean;
	}

	let gameId = '81039240';
	let message = '';
	let username = '';
	let gameData: QuizData;
	let gameMeta: GameMeta = {
		started: false
	};

	let question_index = '';

	let unique = {};

	// function restart() {
	// 	unique = {}; // every {} is unique, {} === {} evaluates to false
	// }

	const connect = () => {
		socket.emit('join_game', { game_pin: gameId, username: username });
	};

	const sendMessage = () => {
		socket.emit('message', message);
		message = '';
	};

	socket.on('joined_game', (data) => {
		console.log('joined_game', data);
		gameData = JSON.parse(data);
	});
	socket.on('game_not_found', (data) => {
		console.log(data, 'game not found');
	});

	socket.on('join_game', (data) => {
		console.log(data, 'join_game');
	});

	socket.on('message', (data) => {
		console.log(data, 'message');
	});

	socket.on('start_game', () => {
		gameMeta.started = true;
	});
</script>

{#if !gameMeta.started}
	<input bind:value={gameId} placeholder="GameID" />
	<input bind:value={username} placeholder="Username" />

	<button on:click={connect}>Connect</button>

	<br />
	<input bind:value={message} placeholder="message" />
	<button on:click={sendMessage}>Send Message</button>
{:else if question_index === ''}
	<Title bind:description={gameData.description} bind:title={gameData.title} />
{:else}
	{#key unique}
		<Question
			bind:question={gameData.questions[parseInt(question_index)]}
			bind:question_index
		/>
	{/key}
{/if}
