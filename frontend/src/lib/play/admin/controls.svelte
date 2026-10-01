<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import ConfirmAction from '$lib/components/ConfirmAction.svelte';
	import Flag from '@lucide/svelte/icons/flag';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import type { GameState } from '$lib/play/admin/game_state.ts';

	interface Props {
		bg_color: string;
		socket_game_controls: SocketGameControls;
		game_token: string;
		game_state: GameState;
	}

	let { bg_color, socket_game_controls, game_token, game_state = $bindable() }: Props = $props();

	const { t } = getLocalization();

	const show_solutions = () => {
		socket_game_controls.show_solutions();
		game_state.timer_res = '0';
	};

	// The answers are up, the scoreboard has not been asked for yet, and there is a
	// scoreboard to show. A slide and a hide-results question have no standings moment.
	const show_scoreboard_step = $derived(
		!game_state.scoreboard_open &&
			game_state.timer_res === '0' &&
			game_state.selected_question !== -1 &&
			game_state.question_results !== null &&
			game_state.question_results !== undefined &&
			JSON.stringify(game_state.final_results) === JSON.stringify([null]) &&
			game_state.quiz_data?.questions?.[game_state.selected_question]?.type !==
				QuizQuestionType.SLIDE &&
			game_state.quiz_data?.questions?.[game_state.selected_question]?.hide_results !== true
	);
</script>

<!-- Was a two-column grid whose button cell asked for col-start-3, a column that
     does not exist, so the one control the host actually uses ended up wherever the
     browser put it. A flex row with space-between says what is meant. -->
<div
	class="fixed inset-x-0 top-0 z-20 flex h-12 items-center justify-between gap-3 px-3"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<!-- Question position is the most-referenced state on a projector screen, so
	     it gets a legible pill rather than 14px of body text in the corner. -->
	<div class="flex items-center gap-2">
		<p
			class="rounded-full border border-border bg-card/80 px-3 py-1
				text-base font-semibold tabular-nums shadow-sm backdrop-blur"
			aria-live="polite"
		>
			<span class="sr-only">Question </span>{game_state.selected_question === -1
				? '0'
				: game_state.selected_question + 1}<span class="text-muted-foreground"
				>&nbsp;/&nbsp;{game_state.quiz_data.questions.length}</span
			>
		</p>
		<!-- Ending early is the final-results path the last question already takes, so
		     players get the podium for what they played rather than a dead screen. -->
		{#if JSON.stringify(game_state.final_results) === JSON.stringify([null])}
			<ConfirmAction
				title={$t('admin_page.end_confirm_title')}
				body={$t('admin_page.end_confirm_body')}
				confirmLabel={$t('admin_page.end_game')}
				cancelLabel={$t('admin_page.keep_playing')}
				onconfirm={() => socket_game_controls.get_final_results()}
				class="bg-card/80 backdrop-blur"
			>
				<Flag />
				{$t('admin_page.end_game')}
			</ConfirmAction>
		{/if}
	</div>
	<div>
		<!-- The standings get their own step between the answers and the next question,
		     the way Kahoot sequences a round: show the answers, then who is winning, then
		     move on. `scoreboard_open` is host-side only -- nothing new crosses the socket,
		     because the totals are already here. -->
		{#if show_scoreboard_step}
			<button
				onclick={() => (game_state.scoreboard_open = true)}
				class="admin-button"
				>{$t('admin_page.show_scoreboard')}
			</button>
		{:else if game_state.selected_question + 1 === game_state.quiz_data.questions.length && ((game_state.timer_res === '0' && game_state.question_results !== null) || game_state.quiz_data?.questions?.[game_state.selected_question]?.type === QuizQuestionType.SLIDE)}
			{#if JSON.stringify(game_state.final_results) === JSON.stringify([null])}
				<button
					onclick={() => socket_game_controls.get_final_results()}
					class="admin-button"
					>{$t('admin_page.get_final_results')}
				</button>
			{/if}
		{:else if game_state.timer_res === '0' || game_state.selected_question === -1}
			{#if (game_state.selected_question + 1 !== game_state.quiz_data.questions.length && game_state.question_results !== null) || game_state.selected_question === -1}
				<button
					onclick={() => {
						game_state.scoreboard_open = false;
						socket_game_controls.set_question_number(game_state.selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', {
						question: game_state.selected_question + 2
					})}
				</button>
			{/if}
			{#if game_state.question_results === null && game_state.selected_question !== -1}
				{#if game_state.quiz_data.questions[game_state.selected_question].type === QuizQuestionType.SLIDE}
					<button
						onclick={() => {
							socket_game_controls.set_question_number(
								game_state.selected_question + 1
							);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', {
							question: game_state.selected_question + 2
						})}
					</button>
				{:else if game_state.quiz_data.questions[game_state.selected_question]?.hide_results === true}
					<button
						onclick={() => {
							socket_game_controls.get_question_results(
								game_token,
								game_state.shown_question_now
							);
							setTimeout(() => {
								socket_game_controls.set_question_number(
									game_state.selected_question + 1
								);
							}, 200);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', {
							question: game_state.selected_question + 2
						})}
					</button>
				{:else}
					<button
						onclick={() =>
							socket_game_controls.get_question_results(
								game_token,
								game_state.shown_question_now
							)}
						class="admin-button"
						>{$t('admin_page.show_results')}
					</button>
				{/if}
			{/if}
		{:else if game_state.selected_question !== -1}
			{#if game_state.quiz_data.questions[game_state.selected_question].type === QuizQuestionType.SLIDE}
				<button
					onclick={() => {
						socket_game_controls.set_question_number(game_state.selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', {
						question: game_state.selected_question + 2
					})}
				</button>
			{:else}
				<button onclick={show_solutions} class="admin-button"
					>{$t('admin_page.stop_time_and_solutions')}
				</button>
			{/if}
		{/if}
	</div>
</div>
