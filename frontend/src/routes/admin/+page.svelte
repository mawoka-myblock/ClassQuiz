<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { socket } from '$lib/socket';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import SomeAdminScreen from '$lib/admin.svelte';
	import GameNotStarted from '$lib/play/admin/game_not_started.svelte';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';
	import FinalResults from '$lib/play/admin/final_results.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { page } from '$app/state';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import { IGameState } from '$lib/play/admin/game_state.ts';
	import { QuizQuestionType } from '$lib/quiz_types';

	navbarVisible.visible = false;

	const { t } = getLocalization();

	// let gameData = {
	// 	game_id: 'a7ddb6af-79ab-45e0-b996-6254c1ad9818',
	// 	game_pin: '66190765'

	interface Props {
		// };
		data: any;
	}

	class GameState implements IGameState {
		public game_id: string;
		public players: Player[];
		public player_scores: Record<string, number>;
		public selected_question: number;
		public timer_res: string;
		public question_results: any;
		public answer_count: number;
		public shown_question_now: number;
		public final_results: Array<null> | Array<Array<PlayerAnswer>>;
		public game_started: boolean;
		public quiz_data: QuizData;
		public control_visible: boolean;

		constructor(game_id: string) {
			this.game_id = game_id;
			this.players = $state([]);
			this.player_scores = $state({});
			this.selected_question = $state(-1);
			this.timer_res = $state(undefined);
			this.quiz_data = $state(null);
			this.control_visible = $state(true);
			this.shown_question_now = $state(-1);
			this.final_results = $state([null]);
			this.game_started = $state(false);
			this.question_results = $state(null);
			this.answer_count = $state(0);
		}

		isGameReadyToStart(): boolean {
			return !this.game_started && this.players.length > 0;
		}

		isGameStarting(): boolean {
			return this.game_started && this.selected_question === -1;
		}

		isActiveQuestionLastQuestion(): boolean {
			return this.selected_question + 1 === this.quiz_data.questions.length;
		}

		isQuestionResultsVisible(): boolean {
			return this.timer_res === '0' && this.question_results !== null
		}

		isActiveQuestionSlide(): boolean {
			return this.quiz_data?.questions?.[this.selected_question]?.type === QuizQuestionType.SLIDE;
		}

		isQuestionEnded(): boolean {
			return this.timer_res === '0' && this.question_results === null && this.selected_question !== -1;
		}

		isQuestionStillOngoing(): boolean {
			return this.timer_res !== '0' && this.selected_question !== -1;
		}
	}

	let { data }: Props = $props();
	let game_mode = $state();
	let { auto_connect, game_token } = $state(data);
	const game_pin = data.game_pin;
	let errorMessage = $state('');
	let success = $state(false);
	let dataexport_download_a = $state();
	let warnToLeave = true;
	let export_token = $state(undefined);


	const socket_game_controls: SocketGameControls = new SocketGameControls(socket);
	let game_state: GameState = $state(new GameState(game_token));

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
	socket.on('session_id', (d) => {
		const session_id = d.session_id;
	});

	socket.on('registered_as_admin', (data) => {
		game_state.quiz_data = JSON.parse(data['game']);
		console.log(game_state.quiz_data);
		success = true;
	});
	socket.on('player_joined', (int_data) => {
		game_state.players = [...game_state.players, int_data];
	});
	socket.on('already_registered_as_admin', () => {
		// eslint-disable-next-line @typescript-eslint/ban-ts-comment
		// @ts-ignore
		errorMessage = $t('admin_page.already_registered_as_admin');
	});

	socket.on('start_game', (_) => {
		game_state.game_started = true;
	});

	socket.on('control_visibility', (data) => {
		game_state.control_visible = data.visible;
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

	const request_answer_export = (e: Event) => {
		e.preventDefault();
		socket.emit('get_export_token');
	};
	const save_quiz = () => {
		socket.emit('save_quiz');
	};

	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	let bg_color = $derived(game_state.quiz_data ? game_state.quiz_data.background_color : undefined);
	let bg_image = $derived(game_state.quiz_data ? game_state.quiz_data.background_image : undefined);
	let results_saved = $state(false);

	let show_final_results = $derived(JSON.stringify(game_state.final_results) !== JSON.stringify([null]));

	// This function in called in every keyboard event in this page
	const next_action = (e: KeyboardEvent) => {
		if((e.key in ["Enter", " "])) return; // Don't catch events other than enter or spacebar

		if(game_state.isGameReadyToStart()) {
			socket_game_controls.start_game()
		}

		else if(game_state.isActiveQuestionLastQuestion() && (game_state.isQuestionResultsVisible() || game_state.isActiveQuestionSlide())){
			socket_game_controls.get_final_results();
		}

		else if(game_state.isGameStarting() || game_state.isQuestionResultsVisible() || game_state.isActiveQuestionSlide()) {
			socket_game_controls.set_question_number(game_state.selected_question + 1);
		}

		else if(game_state.isQuestionStillOngoing()) {
			socket_game_controls.show_solutions();
			game_state.timer_res = '0';
		}

		else if(game_state.isQuestionEnded()) {
			socket_game_controls.get_question_results(game_token, game_state.shown_question_now);
		}

		else {
			console.warn('No action available for this event');
		}
	};
</script>

<svelte:window onbeforeunload={confirmUnload} on:keydown={next_action} />
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
	{#if JSON.stringify(game_state.final_results) !== JSON.stringify([null])}
		{#if game_state.control_visible}
			<div class="w-screen flex justify-center mt-16">
				<div class="w-fit">
					{#if export_token === undefined}
						<GrayButton onclick={request_answer_export}
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
					<GrayButton onclick={save_quiz} flex={true} disabled={results_saved}>
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
		<FinalResults bind:data={game_state.player_scores} {show_final_results} />
	{/if}
	{#if !success}
		{#if errorMessage !== ''}
			<p class="text-red-700">{errorMessage}</p>
		{/if}
	{:else if !game_state.game_started}
		<GameNotStarted
			{game_pin}
			bind:game_state
			{socket_game_controls}
			cqc_code={page.url.searchParams.get('cqc_code')}
		/>
	{:else}
		<SomeAdminScreen
			{game_token}
			{bg_color}
			bind:game_state
		/>
	{/if}
</div>
<a
	onclick={request_answer_export}
	href="#"
	target="_blank"
	bind:this={dataexport_download_a}
	download=""
	class="absolute -top-3/4 -left-3/4 opacity-0">Download</a
>