<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import type { Socket } from 'socket.io-client';
	import { getLocalization } from '$lib/i18n';

	export let bg_color: string;
	export let selected_question: number;
	export let quiz_data: QuizData;
	export let timer_res: string;
	export let final_results;
	export let socket: Socket;

	export let game_token: string;

	export let question_results;

	export let shown_question_now: number;

	const { t } = getLocalization();
	const set_question_number = (q_number: number) => {
		socket.emit('set_question_number', q_number.toString());
	};

	const get_question_results = () => {
		socket.emit('get_question_results', {
			game_id: game_token,
			question_number: shown_question_now
		});
	};
	const show_solutions = () => {
		socket.emit('show_solutions', {});
		timer_res = '0';
	};

	const get_final_results = () => {
		socket.emit('get_final_results', {});
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
				<button on:click={get_final_results} class="admin-button"
					>{$t('admin_page.get_final_results')}
				</button>
			{/if}
		{:else if timer_res === '0' || selected_question === -1}
			{#if (selected_question + 1 !== quiz_data.questions.length && question_results !== null) || selected_question === -1}
				<button
					on:click={() => {
						set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{/if}
			{#if question_results === null && selected_question !== -1}
				{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
					<button
						on:click={() => {
							set_question_number(selected_question + 1);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else if quiz_data.questions[selected_question]?.hide_results === true}
					<button
						on:click={() => {
							get_question_results();
							setTimeout(() => {
								set_question_number(selected_question + 1);
							}, 200);
						}}
						class="admin-button"
						>{$t('admin_page.next_question', { question: selected_question + 2 })}
					</button>
				{:else}
					<button on:click={get_question_results} class="admin-button"
						>{$t('admin_page.show_results')}
					</button>
				{/if}
			{/if}
		{:else if selected_question !== -1}
			{#if quiz_data.questions[selected_question].type === QuizQuestionType.SLIDE}
				<button
					on:click={() => {
						set_question_number(selected_question + 1);
					}}
					class="admin-button"
					>{$t('admin_page.next_question', { question: selected_question + 2 })}
				</button>
			{:else}
				<button on:click={show_solutions} class="admin-button"
					>{$t('admin_page.stop_time_and_solutions')}
				</button>
			{/if}
		{/if}
	</div>
</div>
