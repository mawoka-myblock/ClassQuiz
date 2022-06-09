<script context="module" lang="ts">
	export async function load({ session, url }) {
		if (!session.authenticated) {
			return {
				status: 302,
				redirect: '/account/login'
			};
		}
		const token = url.searchParams.get('token');
		const pin = url.searchParams.get('pin');
		let auto_connect = url.searchParams.get('connect') !== null;
		if (token === null || pin === null) {
			auto_connect = false;
		}
		return {
			props: {
				game_pin: pin === null ? '' : pin,
				game_token: token === null ? '' : token,
				auto_connect: auto_connect
			}
		};
	}
</script>

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';

	import { socket } from '$lib/socket';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores';

	navbarVisible.set(false);

	const { t } = getLocalization();

	// let gameData = {
	// 	game_id: 'a7ddb6af-79ab-45e0-b996-6254c1ad9818',
	// 	game_pin: '66190765'
	// };
	export let game_pin: string;
	export let auto_connect: boolean;
	export let game_token: string;

	interface Player {
		username: string;
	}

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	let players: Array<Player> = [];
	let errorMessage = '';
	let game_started = false;
	let quiz_data: QuizData;
	//let question_number = '0';
	let question_results = null;
	let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let success = false;
	let selected_question = -1;
	let timer_res: string;
	let dataexport_download_a;
	let warnToLeave = true;

	let shown_question_now: number;
	const connect = () => {
		socket.emit('register_as_admin', {
			game_pin: game_pin,
			game_id: game_token
		});
	};
	if (auto_connect) {
		connect();
	}
	socket.on('registered_as_admin', (data) => {
		quiz_data = JSON.parse(data['game']);
		console.log(quiz_data);
		success = true;
	});
	socket.on('player_joined', (data) => {
		players = [...players, data];
	});
	socket.on('already_registered_as_admin', () => {
		errorMessage = $t('admin_page.already_registered_as_admin');
	});
	const set_question_number = (q_number: number) => {
		question_results = null;
		socket.emit('set_question_number', q_number.toString());
		shown_question_now = q_number;
		timer_res = quiz_data.questions[q_number].time;
		selected_question += 1;
		timer(timer_res);
	};

	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: game_token,
			question_number: shown_question_now
		});
		timer_res = '0';
	};

	const getWinnersSorted = () => {
		let winners = {};
		let q_count = quiz_data.questions.length;
		for (let i = 0; i < q_count; i++) {
			let q_res = final_results[i];
			if (q_res === null) {
				continue;
			}
			for (let j = 0; j < q_res.length; j++) {
				let res = q_res[j];
				if (res['right']) {
					if (winners[res['username']] === undefined) {
						winners[res['username']] = 0;
					}
					winners[res['username']] += 1;
				}
			}
		}

		function sortObjectbyValue(obj) {
			const asc = false;
			const ret = {};
			Object.keys(obj)
				.sort((a, b) => obj[asc ? a : b] - obj[asc ? b : a])
				.forEach((s) => (ret[s] = obj[s]));
			return ret;
		}

		return sortObjectbyValue(winners);
	};

	socket.on('question_results', (data) => {
		try {
			data = JSON.parse(data);
		} catch (e) {
			console.error('Failed to parse question results');
			return;
		}
		question_results = data;
	});
	socket.on('export_token', (data) => {
		warnToLeave = false;
		dataexport_download_a.href = `/api/v1/quiz/export_data/${data}?ts=${new Date().getTime()}&game_pin=${game_pin}`;
		dataexport_download_a.click();
		warnToLeave = true;
	});

	const get_final_results = () => {
		socket.emit('get_final_results', {});
	};

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results = data;

		console.log(getWinnersSorted());
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
	const confirmUnload = () => {
		if (warnToLeave) {
			event.preventDefault();
			event.returnValue = '';
		}
	};

	const get_question_title = (q_number: number): string => {
		if (q_number - 1 === quiz_data.questions.length) {
			return;
		}
		try {
			return quiz_data.questions[q_number].question;
		} catch (e) {
			return '';
		}
	};
	const request_answer_export = async () => {
		await socket.emit('get_export_token');
	};
</script>

<svelte:window on:beforeunload={confirmUnload} />
<svelte:head>
	<title>ClassQuiz - Host</title>
</svelte:head>

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
		src="/api/v1/utils/qr/{quiz_data.game_pin}?ref=qr"
		class="block mx-auto w-1/6"
	/>
	<p class="text-3xl text-center">{$t('words.pin')}: {quiz_data.game_pin}</p>
	<ul>
		{#if players.length > 0}
			{#each players as player}
				<li>
					<span>{player.username} </span>
					<button>{$t('words.kick')}</button>
				</li>
			{/each}
		{/if}
	</ul>
	{#if players.length > 0}
		<button
			id="startGame"
			on:click={() => {
				socket.emit('start_game', '');
				game_started = true;
			}}
			>{$t('admin_page.start_game')}
		</button>
	{/if}
{:else}
	{#if timer_res === undefined}
		<span>Select a question to start!</span>
	{:else}
		<span>{$t('admin_page.time_left')}: {timer_res}</span>
	{/if}
	<br />
	{#if timer_res === '0'}
		{#if question_results === null}
			<button on:click={get_question_results} id="GetQuestionResults"
				>{$t('admin_page.get_results')}</button
			>
			<br />
		{:else}
			<br />
			<ul>
				{#each question_results as result}
					<li>{result.username} - {result.answer} - {result.right}</li>
				{/each}
			</ul>
		{/if}
	{:else if timer_res !== undefined}
		<button on:click={get_question_results} id="GetQuestionResultsAndStopTime"
			>{$t('admin_page.get_results_and_stop_time')}</button
		>
	{/if}
	<br />
	<!--{#each quiz_data.questions as { question }, index}
		<button
			on:click={() => {
				set_question_number(index);
			}}>{index}: {question}</button
		>
		<br />
	{/each}-->
	{#if get_question_title(selected_question + 1) !== ''}
		<button
			disabled={!(timer_res === undefined || timer_res === '0')}
			id="SetQuestionNumber"
			on:click={() => {
				set_question_number(selected_question + 1);
			}}>{selected_question + 1}: {get_question_title(selected_question + 1)}</button
		>
		<br />
	{:else}
		<button on:click={get_final_results}>{$t('admin_page.get_final_results')}</button>
	{/if}
{/if}
{#if JSON.stringify(final_results) !== JSON.stringify([null])}
	<button on:click={request_answer_export}>{$t('admin_page.export_results')}</button>
	{#await import('$lib/play/end.svelte') then c}
		<svelte:component this={c.default} bind:final_results bind:quiz_data />
	{/await}
{/if}
<a
	on:click|preventDefault={request_answer_export}
	href="#"
	bind:this={dataexport_download_a}
	class="absolute -top-3/4 -left-3/4 opacity-0">Download</a
>
