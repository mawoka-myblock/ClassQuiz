<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { page } from '$app/stores';
	import { socket } from '$lib/socket';
	import type { QuizData } from '$lib/quiz_types';
	import { QuizQuestionType } from '$lib/quiz_types.js';
	import Spinner from '$lib/Spinner.svelte';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores';

	const data = {
		game_pin: $page.url.searchParams.get('game_pin'),
		game_id: $page.url.searchParams.get('game_id')
	};

	navbarVisible.set(false);

	const { t } = getLocalization();
	let timer_interval;
	let timer_res = undefined;
	let selected_question = -1;
	let game_started = false;
	let question_results;
	let final_results = [null];
	let warnToLeave = true;
	let dataexport_download_a;

	let players: Array<{ sid: string; username: string }> = [];

	let game_data: QuizData;
	let shown_question_now;
	let control_visible = false;

	if (!data.game_id || !data.game_pin) {
		console.log('Error!');
	} else {
		socket.emit('register_as_remote', data);
	}

	const timer = (time: string) => {
		let seconds = Number(time);
		timer_interval = setInterval(() => {
			if (timer_res === '0') {
				clearInterval(timer_interval);
				// socket.emit('show_solutions', {});
				return;
			} else {
				seconds--;
			}

			timer_res = seconds.toString();
		}, 1000);
	};

	const confirmUnload = (e: Event) => {
		if (warnToLeave) {
			e.preventDefault();
			// eslint-disable-next-line @typescript-eslint/ban-ts-comment
			// @ts-ignore
			e.returnValue = '';
		}
	};

	const set_question_number = (q_number: number) => {
		socket.emit('set_question_number', q_number.toString());
	};

	const start_game = () => {
		socket.emit('start_game', '');
	};

	const get_question_results = () => {
		socket.emit('get_question_results', {
			question_number: shown_question_now
		});
	};

	const show_solutions = () => {
		socket.emit('show_solutions', {});
	};
	const get_final_results = () => {
		socket.emit('get_final_results', {});
	};

	const request_answer_export = async () => {
		await socket.emit('get_export_token');
	};

	const get_already_joined_players = async () => {
		console.log('GETTING PLAYERS');
		const res = await fetch(
			`/api/v1/live/players?game_pin=${data.game_pin}&game_id=${data.game_id}`
		);
		if (res.ok) {
			players = await res.json();
		}
	};

	let circular_progress = 0;
	$: {
		try {
			circular_progress =
				1 -
				((100 / game_data.questions[selected_question].time) * parseInt(timer_res)) / 100;
		} catch {
			circular_progress = 0;
		}
	}

	socket.on('solutions', (_) => {
		timer_res = '0';
		clearInterval(timer_interval);
	});
	socket.on('question_results', (_) => {
		timer_res = '0';
		clearInterval(timer_interval);
	});
	socket.on('registered_as_admin', (data) => {
		game_data = JSON.parse(data.game);
	});

	socket.on('start_game', (_) => {
		game_started = true;
	});

	socket.on('control_visibility', (data) => {
		control_visible = data.visible;
	});

	socket.on('question_results', (data) => {
		try {
			question_results = JSON.parse(data);
			timer_res = '0';
		} catch {
			question_results = undefined;
		}
	});
	socket.on('set_question_number', (data) => {
		timer_res = '0';
		clearInterval(timer_interval);
		question_results = null;
		shown_question_now = data.question_index;
		timer_res = game_data.questions[data.question_index].time;
		selected_question = selected_question + 1;
		timer(timer_res);
	});

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results = data;
	});

	socket.on('everyone_answered', (_) => {
		timer_res = '0';
	});

	socket.on('export_token', (int_data) => {
		warnToLeave = false;
		dataexport_download_a.href = `/api/v1/quiz/export_data/${int_data}?ts=${new Date().getTime()}&game_pin=${
			game_data.game_pin
		}`;
		dataexport_download_a.click();
		setTimeout(() => {
			warnToLeave = true;
		}, 200);
	});

	socket.on('player_joined', (data) => {
		players = [...players, data];
	});
</script>

<svelte:window on:beforeunload={confirmUnload} />
{#if game_started}
	{#if selected_question + 1 === game_data.questions.length && ((timer_res === '0' && question_results !== null) || game_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
		{#if JSON.stringify(final_results) === JSON.stringify([null])}
			<button on:click={get_final_results} class="admin-button">Get final results </button>
		{:else}
			<div class="w-screen flex justify-center mt-16">
				<button on:click={request_answer_export} class="admin-button"
					>{$t('admin_page.export_results')}</button
				>
			</div>
		{/if}
	{:else if timer_res === '0' || selected_question === -1}
		{#if (selected_question + 1 !== game_data.questions.length && question_results !== null) || selected_question === -1}
			<button
				on:click={() => {
					set_question_number(selected_question + 1);
				}}
				class="admin-button"
				>Next Question ({selected_question + 2})
			</button>
		{/if}
		{#if question_results === null && selected_question !== -1}
			{#if game_data.questions[selected_question].type === QuizQuestionType.SLIDE}
				<button
					on:click={() => {
						set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>Next Question ({selected_question + 2})
				</button>
			{:else}
				<button on:click={get_question_results} class="admin-button">Show results </button>
			{/if}
		{/if}
	{:else if selected_question !== -1}
		{#if game_data.questions[selected_question].type === QuizQuestionType.SLIDE}
			<button
				on:click={() => {
					set_question_number(selected_question + 1);
				}}
				class="admin-button"
				>Next Question ({selected_question + 2})
			</button>
		{:else}
			<button on:click={show_solutions} class="admin-button"
				>Stop time and show solutions
			</button>
		{/if}
	{/if}
	{#if selected_question === -1}
		<h1>{game_data.title}</h1>
		<p>{game_data.description}</p>
	{:else if game_data.questions[selected_question].type === QuizQuestionType.SLIDE}
		{#await import('$lib/play/admin/slide.svelte')}
			<Spinner my_20={false} />
		{:then c}
			<svelte:component
				this={c.default}
				bind:question={game_data.questions[selected_question]}
			/>
		{/await}
	{:else}
		<div class="flex flex-col justify-center w-screen h-1/6">
			<h1 class="text-6xl text-center">
				{@html game_data.questions[selected_question].question}
			</h1>
			<!--			<span class='text-center py-2 text-lg'>{$t('admin_page.time_left')}: {timer_res}</span>-->
			<div class="mx-auto my-2">
				<CircularTimer
					bind:text={timer_res}
					bind:progress={circular_progress}
					color="#ef4444"
				/>
			</div>
			{#if game_data.questions[selected_question].image !== null}
				<div>
					<img
						src="/api/v1/storage/download/{game_data.questions[selected_question]
							.image}"
						class="max-h-[20vh] object-cover mx-auto mb-8 w-auto"
						alt="Content for Question"
					/>
				</div>
			{/if}
			{#if game_data.questions[selected_question].type === QuizQuestionType.ABCD || game_data.questions[selected_question].type === QuizQuestionType.VOTING}
				<div class="grid grid-cols-2 gap-2 w-full p-4">
					{#each game_data.questions[selected_question].answers as answer, i}
						<div
							class="rounded-lg h-fit flex"
							style="background-color: {answer.color ?? '#B45309'}"
							class:opacity-50={!answer.right &&
								game_data.questions[selected_question].type ===
									QuizQuestionType.ABCD}
						>
							<span class="text-center text-2xl px-2 py-4 w-full text-black"
								>{answer.answer}</span
							>
							<span class="pl-4 w-10" />
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}

	{#if timer_res === '0' && JSON.stringify(final_results) === JSON.stringify( [null] ) && game_data.questions[selected_question].type !== QuizQuestionType.SLIDE}
		{#if game_data.questions[selected_question].type === QuizQuestionType.VOTING && question_results}
			{#await import('$lib/play/admin/voting_results.svelte')}
				<Spinner />
			{:then c}
				<svelte:component
					this={c.default}
					bind:data={question_results}
					bind:question={game_data.questions[selected_question]}
				/>
			{/await}
		{/if}
	{/if}
{:else}
	<button on:click={start_game} class="admin-button">Start Game!</button>

	<h2>Players:</h2>
	{#await get_already_joined_players()}
		<Spinner my_20={false} />
	{:then _}
		<div>
			<ul>
				{#each players as player}
					<li>{player.username}</li>
				{/each}
			</ul>
		</div>
	{/await}
{/if}
<div class="fixed top-0 right-0">
	{#if control_visible}
		<button
			on:click={() => {
				socket.emit('set_control_visibility', { visible: false });
			}}
			>Hide Controls
		</button>
	{:else}
		<button
			on:click={() => {
				socket.emit('set_control_visibility', { visible: true });
			}}
			>Show Controls
		</button>
	{/if}
</div>

<a
	on:click|preventDefault={request_answer_export}
	href="#"
	bind:this={dataexport_download_a}
	class="absolute -top-3/4 -left-3/4 opacity-0 hidden">Download</a
>
