<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizQuestionType } from '$lib/quiz_types';
	import type { QuizData } from '$lib/quiz_types';
	import { get_foreground_color } from '$lib/helpers.js';
	import { kahoot_icons } from '$lib/play/kahoot_mode_assets/kahoot_icons.js';
	import CircularTimer from '$lib/play/circular_progress.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { getLocalization } from '$lib/i18n';

	export let quiz_data: QuizData;
	export let selected_question: number;
	export let timer_res: string;

	export let answer_count: number;
	export let default_colors: string[];

	const { t } = getLocalization();

	let circular_progress = 0;
	$: {
		try {
			circular_progress =
				1 -
				((100 / parseInt(quiz_data.questions[selected_question].time)) *
					parseInt(timer_res)) /
					100;
		} catch {
			circular_progress = 0;
		}
	}
</script>

<div class="flex flex-col justify-center w-screen h-1/6">
	<h1 class="text-6xl text-center">
		{@html quiz_data.questions[selected_question].question}
	</h1>
	<!--			<span class='text-center py-2 text-lg'>{$t('admin_page.time_left')}: {timer_res}</span>-->
	<div class="grid grid-cols-3 my-2">
		<span />
		<div class="m-auto">
			<CircularTimer
				bind:text={timer_res}
				bind:progress={circular_progress}
				color="#ef4444"
			/>
		</div>
		<p class="m-auto text-3xl">
			{$t('admin_page.answers_submitted', { answer_count: answer_count })}
		</p>
	</div>
</div>
{#if quiz_data.questions[selected_question].image !== null}
	<div class="flex w-full">
		<MediaComponent
			src={quiz_data.questions[selected_question].image}
			muted={false}
			css_classes="max-h-[20vh] object-cover mx-auto mb-8 w-auto"
		/>
	</div>
{/if}
{#if quiz_data.questions[selected_question].type === QuizQuestionType.ABCD || quiz_data.questions[selected_question].type === QuizQuestionType.VOTING || quiz_data.questions[selected_question].type === QuizQuestionType.CHECK}
	<div class="grid grid-rows-2 grid-flow-col auto-cols-auto gap-2 w-full p-4">
		{#each quiz_data.questions[selected_question].answers as answer, i}
			<div
				class="rounded-lg h-fit flex border-2 border-black"
				style="background-color: {answer.color ?? default_colors[i]};"
				class:opacity-50={!answer.right &&
					timer_res === '0' &&
					quiz_data.questions[selected_question].type === QuizQuestionType.ABCD}
			>
				<img
					class="w-14 inline-block pl-4"
					alt="icon"
					style="color: {get_foreground_color(answer.color ?? default_colors[i])}"
					src={kahoot_icons[i]}
				/>
				<span
					class="text-center text-2xl px-2 py-4 w-full"
					style="color: {get_foreground_color(answer.color ?? default_colors[i])}"
					>{answer.answer}</span
				>
				<span class="pl-4 w-10" />
			</div>
		{/each}
	</div>
{:else if quiz_data.questions[selected_question].type === QuizQuestionType.TEXT}
	{#if timer_res === '0'}
		<div class="grid grid-cols-2 gap-2 w-full p-4">
			{#each quiz_data.questions[selected_question].answers as answer, i}
				<div class="rounded-lg h-fit flex bg-[#B07156]">
					<span class="text-center text-2xl px-2 py-4 w-full text-black"
						>{answer.answer}</span
					>
					<span class="pl-4 w-10" />
				</div>
			{/each}
		</div>
	{:else}
		<div class="flex justify-center">
			<p class="text-2xl">{$t('admin_page.enter_answer_into_field')}</p>
		</div>
	{/if}
{/if}
