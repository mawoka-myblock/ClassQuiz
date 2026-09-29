<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Check from '@lucide/svelte/icons/check';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import { socket } from '$lib/socket';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import SomeAdminScreen from '$lib/admin.svelte';
	import GameNotStarted from '$lib/play/admin/game_not_started.svelte';
	import { onMount } from 'svelte';
	import FinalResults from '$lib/play/admin/final_results.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';
	import { page } from '$app/state';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import type { IGameState } from '$lib/play/admin/game_state.ts';
	import { QuizQuestionType, type QuizData } from '$lib/quiz_types';
	import type { Player, PlayerAnswer } from '$lib/admin';
	import { tinykeys } from '$lib/tinykeys';

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

		is_game_ready_to_start(): boolean {
			return !this.game_started && this.players.length > 0;
		}

		is_game_starting(): boolean {
			return this.game_started && this.selected_question === -1;
		}

		is_active_question_last_question(): boolean {
			return this.selected_question + 1 === this.quiz_data.questions.length;
		}

		is_question_results_visible(): boolean {
			return this.timer_res === '0' && this.question_results !== null;
		}

		is_active_question_slide(): boolean {
			return (
				this.quiz_data?.questions?.[this.selected_question]?.type === QuizQuestionType.SLIDE
			);
		}

		is_question_ended(): boolean {
			return (
				this.timer_res === '0' &&
				this.question_results === null &&
				this.selected_question !== -1
			);
		}

		is_question_still_ongoing(): boolean {
			return this.timer_res !== '0' && this.selected_question !== -1;
		}
	}

	let { data }: Props = $props();
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
	};
	onMount(() => {
		if (auto_connect) {
			connect();
			// A reconnect gets a new sid, which the server doesn't know as the admin
			// of this game, so re-register or no player event ever arrives again.
			socket.on('connect', connect);
		}
		tinykeys(window, {
			Enter: next_action,
			Space: next_action
		});
	});
	socket.on('registered_as_admin', (data) => {
		game_state.quiz_data = JSON.parse(data['game']);
		console.log(game_state.quiz_data);
		game_state.players = data['players'] ?? [];
		success = true;
	});
	socket.on('player_joined', (int_data) => {
		game_state.players = [...game_state.players, int_data];
	});
	socket.on('player_left', (int_data) => {
		game_state.players = game_state.players.filter((p) => p.username !== int_data.username);
	});
	// The server says the lobby is closed; only then leave, so a cancel that never
	// reached it doesn't strand players on a game the host has walked away from.
	socket.on('game_ended', () => {
		warnToLeave = false;
		window.location.assign('/my-quizzes');
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

	let bg_color = $derived(
		game_state.quiz_data ? game_state.quiz_data.background_color : undefined
	);
	let bg_image = $derived(
		game_state.quiz_data ? game_state.quiz_data.background_image : undefined
	);
	let results_saved = $state(false);

	let show_final_results = $derived(
		JSON.stringify(game_state.final_results) !== JSON.stringify([null])
	);

	// This function in called in every keyboard event in this page
	const next_action = () => {
		if (
			game_state.is_active_question_last_question() &&
			(game_state.is_question_results_visible() || game_state.is_active_question_slide())
		) {
			socket_game_controls.get_final_results();
		} else if (
			game_state.is_game_starting() ||
			game_state.is_question_results_visible() ||
			game_state.is_active_question_slide()
		) {
			socket_game_controls.set_question_number(game_state.selected_question + 1);
		} else if (game_state.is_question_still_ongoing()) {
			socket_game_controls.show_solutions();
			game_state.timer_res = '0';
		} else if (game_state.is_question_ended()) {
			socket_game_controls.get_question_results(game_token, game_state.shown_question_now);
		} else {
			console.warn('No action available for this event');
		}
	};
</script>

<svelte:window onbeforeunload={confirmUnload} />
<svelte:head>
	<title>frogQuiz - Host</title>
</svelte:head>
<!-- min-h-dvh, not min-h-screen: 100vh counts browser chrome that is not there on a
     phone, pushing the bottom of the host shell below the fold. -->
<div
	class="min-h-dvh min-w-full"
	style="background-repeat: no-repeat;background-size: 100% 100%;background-image: {bg_image
		? `url('${bg_image}')`
		: `unset`}; background-color: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	{#if JSON.stringify(game_state.final_results) !== JSON.stringify([null])}
		{#if game_state.control_visible}
			<!-- Two separately positioned fixed divs at top-14 and top-[6.5rem], each
			     wrapped in a w-fit that fought GrayButton's own w-full, so the pair
			     rendered as two misaligned pills of different widths hand-placed with
			     magic numbers. One stack, below the h-12 controls bar, both the same
			     width. -->
			<div class="fixed top-16 right-4 z-30 flex w-44 flex-col items-stretch gap-2">
				<!-- "Download results" used to be the only action here, which left the host
				     stuck on the podium with nowhere to go once a game ended. -->
				<!-- /my-quizzes for everyone: it lists account quizzes when signed in and
				     this browser's quizzes when not (D1 in MVP.md). -->
				<GrayButton href="/my-quizzes" flex={true}>
					<ArrowLeft class="size-4" aria-hidden="true" />
					{$t('words.back')}
				</GrayButton>
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
				<!-- Hidden for an anonymous host. The backend writes the GameResults row
				     with user=NULL, and every read path in routers/results.py is
				     user-scoped, so the row it saves is unreachable afterwards. The
				     podium and the spreadsheet export both work without an account and
				     stay. Read from `data`, not the `signedIn` store -- see +page.server.ts. -->
				{#if data.signed_in}
					<GrayButton onclick={save_quiz} flex={true} disabled={results_saved}>
						{#if results_saved}
							<Check class="size-4" aria-hidden="true" />
							<span class="sr-only">{$t('admin_page.save_results')}</span>
						{:else}{$t('admin_page.save_results')}{/if}
					</GrayButton>
				{/if}
			</div>
		{/if}
		<FinalResults bind:data={game_state.player_scores} {show_final_results} />
	{/if}
	{#if !success}
		{#if errorMessage !== ''}
			<!-- The navbar is hidden on the host screen, so a failed registration used to
			     leave a red line and no way out. -->
			<div class="fq-stage text-center">
				<p class="text-destructive" role="alert">{errorMessage}</p>
				<GrayButton href="/my-quizzes">
					<ArrowLeft class="size-4" aria-hidden="true" />
					{$t('words.back')}
				</GrayButton>
			</div>
		{/if}
	{:else if !game_state.game_started}
		<GameNotStarted
			{game_pin}
			bind:game_state
			{socket_game_controls}
			cqc_code={page.url.searchParams.get('cqc_code')}
		/>
	{:else}
		<SomeAdminScreen {game_token} {bg_color} bind:game_state />
	{/if}
</div>
<a
	onclick={request_answer_export}
	href="#"
	target="_blank"
	bind:this={dataexport_download_a}
	download=""
	class="absolute size-px overflow-hidden whitespace-nowrap opacity-0">Download</a
>
