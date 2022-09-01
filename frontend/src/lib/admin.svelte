<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { get_question_title } from '$lib/admin.ts';
	import type { PlayerAnswer } from '$lib/admin.ts';
	import { socket } from './socket';
	import ShowQuestion from '$lib/play/question.svelte';

	export let game_token: string;
	export let quiz_data: QuizData;

	const { t } = getLocalization();

	let question_results = null;
	export let final_results: Array<null> | Array<Array<PlayerAnswer>> = [null];
	let selected_question = -1;
	let timer_res: string;
	let shown_question_now: number;
	let final_results_clicked = false;

	console.log(quiz_data);

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

	const get_final_results = () => {
		socket.emit('get_final_results', {});
		final_results_clicked = true;
	};

	socket.on('final_results', (data) => {
		// data = JSON.parse(data);
		final_results = data;
	});

	socket.on('question_results', (data) => {
		try {
			question_results = JSON.parse(data);
		} catch {
			question_results = undefined;
		}
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

{#if timer_res !== undefined && !final_results_clicked}
	<div class="flex flex-col justify-center w-screen h-1/6">
		<h1 class="text-6xl text-center">
			{quiz_data.questions[selected_question].question}
		</h1>
		<span class="text-center py-2 text-lg">{$t('admin_page.time_left')}: {timer_res}</span>
	</div>
	{#if quiz_data.questions[selected_question].image !== null}
		<div>
			<img
				src={quiz_data.questions[selected_question].image}
				class="h-2/5 object-cover mx-auto mb-8"
				alt="Content for Question"
			/>
		</div>
	{/if}
{/if}
<br />
{#if timer_res === '0'}
	{#if question_results === null}
		<div class="w-full flex justify-center">
			<button
				on:click={get_question_results}
				id="GetQuestionResults"
				class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
				>{$t('admin_page.get_results')}</button
			>
		</div>
	{:else if question_results === undefined}
		{#if !final_results_clicked}
			<div class="w-full flex justify-center">
				<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
			</div>
		{/if}
	{:else}
		<div class="w-full flex justify-center">
			<div class="relative overflow-x-auto shadow-md rounded-lg">
				<table class="w-fit text-sm text-left text-gray-500 dark:text-gray-400">
					<thead
						class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
					>
						<tr>
							<th scope="col" class="px-6 py-3">
								{$t('words.username')}
							</th>
							<th scope="col" class="px-6 py-3">
								{$t('words.answer')}
							</th>
							<th scope="col" class="px-6 py-3">
								{$t('words.correct')}?
							</th>
						</tr>
					</thead>
					<tbody>
						{#each question_results as result}
							<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
								<th
									scope="row"
									class="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap"
								>
									{result.username}
								</th>
								<td class="px-6 py-4">
									{result.answer}
								</td>
								<td class="px-6 py-4">
									{#if result.right}
										✅
									{:else}
										❌
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
{:else if timer_res !== undefined}
	<div class="w-full flex justify-center">
		<button
			on:click={get_question_results}
			id="GetQuestionResultsAndStopTime"
			class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
			>{$t('admin_page.get_results_and_stop_time')}</button
		>
	</div>
{/if}
<br />
{#if get_question_title(selected_question + 1, quiz_data) !== '' && selected_question + 1 !== 0}
	<div class="w-full flex justify-center">
		<button
			class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
			disabled={!(timer_res === undefined || timer_res === '0')}
			id="SetQuestionNumber"
			on:click={() => {
				set_question_number(selected_question + 1);
			}}
			>{$t('admin_page.show_next_question')}: {get_question_title(
				selected_question + 1,
				quiz_data
			)}</button
		>
	</div>
{:else if selected_question + 1 === 0}
	<div class="w-full flex justify-center">
		<button
			on:click={() => {
				set_question_number(0);
			}}
			class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
		>
			{$t('admin_page.start_by_showing_first_question')}
		</button>
	</div>
{:else if final_results_clicked === false}
	<div class="w-screen flex justify-center">
		<button
			on:click={get_final_results}
			class="px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
			>{$t('admin_page.get_final_results')}</button
		>
	</div>
{/if}
