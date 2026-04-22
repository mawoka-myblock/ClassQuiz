<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { getLocalization } from '$lib/i18n';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import { GameState } from '$lib/play/admin/game_state.ts';

	interface Props {
		bg_color: string;
		selected_question: number;
		quiz_data: QuizData;
		timer_res: string;
		final_results: any;
		socket_game_controls: SocketGameControls;
		game_token: string;
		question_results: any;
		shown_question_now: number;
		game_state: GameState;
	}

	let {
		bg_color,
		selected_question,
		quiz_data,
		timer_res = $bindable(),
		final_results,
		socket_game_controls,
		game_token,
		question_results,
		shown_question_now,
		game_state = $bindable()
	}: Props = $props();

	const { t } = getLocalization();

	const show_solutions = () => {
		socket_game_controls.show_solutions();
		timer_res = '0';
		game_state.timer_res = '0';
	};
</script>

<div
	class="fixed top-0 w-full h-10 z-20 grid grid-cols-2"
	style="background: {bg_color ? bg_color : 'transparent'}"
	class:text-black={bg_color}
>
	<p class="mr-auto ml-0 col-start-1 col-end-1">
		{selected_question === -1 ? '0' : selected_question + 1}
		/{quiz_data.questions.length}
	</p>
	<div class="justify-self-end ml-auto mr-0 col-start-3 col-end-3">
		{#if selected_question + 1 === quiz_data.questions.length && ((timer_res === '0' && question_results !== null) || quiz_data?.questions?.[selected_question]?.type === QuizQuestionType.SLIDE)}
			{#if JSON.stringify(final_results) === JSON.stringify([null])}
				<button onclick={() => socket_game_controls.get_final_results()} class="admin-button"
					>{$t('admin_page.get_final_results')}
				</button>
			{/if}
		{:else if timer_res === '0' || selected_question === -1}
			{#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
				<button
					onclick={() => {
						socket_game_controls.set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{/if}
			{#if question_results === null && selected_question !== -1}
				{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
					<button
						onclick={() => {
							socket_game_controls.set_question_number(selected_question + 1);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else if quiz_data.questions[selected_question]?.hide_results === true}
					<button
						onclick={() => {
							socket_game_controls.get_question_results(game_token, shown_question_now);
							setTimeout(() => {
								socket_game_controls.set_question_number(selected_question + 1);
							}, 200);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else}
					<button onclick={() => socket_game_controls.get_question_results(game_token, shown_question_now)} class="admin-button"
						>{$t('admin_page.show_results')}
					</button>
				{/if}
			{/if}
		{:else if selected_question !== -1}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
				<button
					onclick={() => {
						socket_game_controls.set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{:else}
				<button onclick={show_solutions} class="admin-button"
					>{$t('admin_page.stop_time_and_solutions')}
				</button>
			{/if}
		{/if}
	</div>
</div>
