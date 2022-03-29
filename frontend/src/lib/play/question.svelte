<script lang="ts">
	import type { Question } from '../../app';
	import { socket } from '$lib/socket';

	export let question: Question;
	export let question_index: string | number;

	if (typeof question_index === 'string') {
		question_index = parseInt(question_index);
	} else {
		throw new Error('question_index must be a string or number');
	}

	let timer_res = question.time;
	let selected_answer: string;

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
	console.log(selected_answer);

	timer(question.time);

	const selectAnswer = (answer: string) => {
		selected_answer = answer;
		//timer_res = '0';
		socket.emit('submit_answer', {
			question_index: question_index,
			answer: answer
		});
	};
</script>

<div class="flex flex-col justify-center w-screen h-1/6">
	<h1 class="text-6xl text-center">
		{question.question}
	</h1>
	<span class="text-center py-2 text-lg">{timer_res}</span>
</div>
<div>
	<img src='{question.image}' class="w-full h-full object-cover" alt='Question image'>
</div>
{#if timer_res !== '0'}
	<div class="flex flex-wrap">
		{#each question.answers as answer}
			<button
				class="w-1/2 text-3xl bg-amber-700 my-2 disabled:opacity-60 border border-white"
				disabled={selected_answer !== undefined}
				on:click={() => selectAnswer(answer.answer)}>{answer.answer}</button
			>
		{/each}
	</div>
{:else}
	<div class="flex flex-wrap">
		{#each question.answers as answer}
			{#if answer.right}
				<button
					class="w-1/2 text-3xl bg-green-600 border border-white"
					disabled
					class:opacity-30={answer.answer !== selected_answer}>{answer.answer}</button
				>
			{:else}
				<button
					class="w-1/2 text-3xl bg-red-500 border border-white"
					disabled
					class:opacity-30={answer.answer !== selected_answer}>{answer.answer}</button
				>
			{/if}
		{/each}
	</div>
{/if}
