<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
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
</script>

<div
	class="fixed top-0 w-full h-10 z-20 grid grid-cols-2"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<p class="mr-auto ml-0 col-start-1 col-end-1">
		{game_state.selected_question === -1 ? '0' : game_state.selected_question + 1}
		/{game_state.quiz_data.questions.length}
	</p>
	<div class="justify-self-end ml-auto mr-0 col-start-3 col-end-3">
		{#if game_state.selected_question + 1 === game_state.quiz_data.questions.length && ((game_state.timer_res === '0' && game_state.question_results !== null) || game_state.quiz_data?.questions?.[game_state.selected_question]?.type === QuizQuestionType.SLIDE)}
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
