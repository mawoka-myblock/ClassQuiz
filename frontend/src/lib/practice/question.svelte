<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { fly } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	export let question: Question;

	const { t } = getLocalization();

	let selected_question = undefined;
	let timer_res = question.time;
	let show_results = false;

	// Stop the timer if the question is answered
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

	timer(question.time);
</script>

<div class="w-full px-6 lg:px-20 h-[80vh] absolute" in:fly={{ x: 100 }} out:fly={{ x: -100 }}>
	<h1 class="text-3xl text-center">{question.question}</h1>
	{#if question.image !== null}
		<div>
			<img
				src={question.image}
				class="max-h-[40vh] object-cover mx-auto mb-8 w-auto"
				alt="Content for Question"
			/>
		</div>
	{/if}
	<p class="text-center">{timer_res}</p>
	{#if show_results}
		<div>
			{#each question.answers as answer, i}
				<button
					disabled
					class:bg-green-500={question.answers[i].right}
					class:bg-red-500={!question.answers[i].right}
					class="p-2 rounded-lg flex justify-center w-full transition my-5"
					>{answer.answer}</button
				>
			{/each}
		</div>
	{:else}
		<div>
			{#each question.answers as answer, i}
				<button
					disabled={selected_question !== undefined || timer_res === '0'}
					class="p-2 rounded-lg flex justify-center w-full transition bg-amber-300 my-5 disabled:grayscale"
					on:click={() => {
						selected_question = i;
						timer_res = '0';
					}}>{answer.answer}</button
				>
			{/each}
			{#if timer_res === '0'}
				<button
					class="bg-orange-500 p-2 rounded-lg flex justify-center w-full transition my-5"
					on:click={() => {
						show_results = true;
					}}>{$t('admin_page.get_results')}</button
				>
			{/if}
		</div>
	{/if}
</div>
