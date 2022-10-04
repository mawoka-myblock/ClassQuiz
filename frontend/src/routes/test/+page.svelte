<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { navbarVisible } from '$lib/stores';

	navbarVisible.set(false);
	const data = [
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},

		{
			username: 'Mawoka',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'dewads',
			answer: 'A very long answe-thing',
			right: false,
			time_taken: 1681.631,
			score: 0
		},
		{
			username: 'dsadsa',
			answer: 'der',
			right: false,
			time_taken: 2613.532,
			score: 0
		}
	];
	const quiz_answers = ['A very long answe-thing', 'dieter', 'moin', 'der'];
	let sorted_data = {};
	for (const i of quiz_answers) {
		sorted_data[i] = 0;
	}
	for (const i of data) {
		sorted_data[i.answer] += 1;
	}
</script>

<div class="flex justify-center h-screen w-full">
	<div
		class="m-auto grid grid-rows-3 w-fit gap-4"
		style="grid-template-columns: repeat({quiz_answers.length}, minmax(0, 1fr));"
	>
		{#each quiz_answers as answer}
			<span class="text-center self-end"
				>{#if sorted_data[answer] > 0}{sorted_data[answer]}{/if}</span
			>
		{/each}
		{#each quiz_answers as answer}
			<div
				class="w-20 bg-black self-end flex justify-center"
				style="height: {(sorted_data[answer] * 20) / data.length}rem"
			/>
		{/each}
		{#each quiz_answers as answer}
			<div class="w-20">
				<p class="-rotate-45">{answer}</p>
			</div>
		{/each}
	</div>
</div>
