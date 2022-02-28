<script lang="ts">
	import type { QuizData } from '../app';

	import { socket } from '$lib/socket';

	let gameData = {
		game_id: 'a7ddb6af-79ab-45e0-b996-6254c1ad9818',
		game_pin: '66190765'
	};
	let success = false;
	let players: Array<string> = [];
	let errorMessage = '';
	let game_started = false;
	let quiz_data: QuizData;
	let question_number: string = '0';
	let question_results = null;

	let shown_question_now: number;
	const connect = () => {
		socket.emit('register_as_admin', gameData);
	};
	socket.on('registered_as_admin', (data) => {
		console.log('registered_as_admin', data['game']);
		quiz_data = JSON.parse(data['game']);
		console.log(quiz_data);
		console.log(quiz_data.questions[0].question);
		console.log(quiz_data.questions);
		success = true;
	});
	socket.on('player_joined', (data) => {
		players = [...players, data];
	});
	socket.on('already_registered_as_admin', (data) => {
		errorMessage = 'There is already an admin registered for this game.';
	});
	let timer_res: string;
	const set_question_number = (q_number: number) => {
		question_results = null;
		socket.emit('set_question_number', q_number.toString());
		shown_question_now = q_number;
		timer_res = quiz_data.questions[q_number].time;
		timer(timer_res);
	};

	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: gameData.game_id,
			question_number: shown_question_now
		});
	};

	socket.on('question_results', (data) => {
		data = JSON.parse(data);
		console.log(data);
		question_results = data;
	});

	const timer = (time: string) => {
		let seconds = Number(time);
		let timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};
</script>

{#if !success}
	<input placeholder="game id" bind:value={gameData.game_id} />
	<input placeholder="game pin" bind:value={gameData.game_pin} />
	<button on:click={connect}>Connect!</button>
	{#if errorMessage !== ''}
		<p class="text-red-700">{errorMessage}</p>
	{/if}
{:else if !game_started}
	<ul>
		{#if players.length > 0}
			{#each players as player}
				<li>
					<span>{player.username} </span>
					<button>Kick</button>
				</li>
			{/each}
		{/if}
	</ul>
	{#if players.length > 0}
		<button
			on:click={() => {
				socket.emit('start_game', '');
				game_started = true;
			}}>Start Game</button
		>
	{/if}
{:else}
	<span>Time left: {timer_res}</span>
	<br />
	{#if timer_res === '0'}
		<button on:click={get_question_results}>Get results</button>
		<br />
		{#if question_results !== null}
			<br />
			<ul>
				{#each question_results as result}
					<li>{result.username} - {result.answer} - {result.right}</li>
				{/each}
			</ul>
		{/if}
	{/if}
	<br />
	{#each quiz_data.questions as { question }, index}
		<button
			on:click={() => {
				set_question_number(index);
			}}>{index}: {question}</button
		>
		<br />
	{/each}
{/if}
