<script lang="ts">
	import type { Answer, QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let results: Array<Answer>;
	export let game_data: QuizData;
	export let question_index: string;
	let data_store = {};

	const question = game_data.questions[parseInt(question_index)].answers;
	for (let i = 0; i < question.length; i++) {
		data_store[question[i].answer] = 0;
	}

	for (let i = 0; i < results.length; i++) {
		data_store[results[i].answer] += 1;
	}
</script>

<!-- Show the results from the results object -->
<!-- Language: SvelteHTML -->
<!-- Path: frontend/src/lib/play/show_results.svelte -->

<div>
	<h2 class="text-center text-3xl mb-8">{$t('words.result', { count: 2 })}</h2>
	<div class="w-screen flex justify-center">
		<div class="relative overflow-x-auto shadow-md rounded-lg">
			<table class="w-fit text-sm text-left text-gray-500 dark:text-gray-400">
				<thead class="bg-gray-50 dark:bg-gray-700">
					<tr>
						<th
							scope="col"
							class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
						>
							{$t('words.answer')}
						</th>
						<th
							scope="col"
							class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
						>
							{$t('words.count')}
						</th>
						<th
							scope="col"
							class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
						>
							{$t('words.correct')}
						</th>
					</tr>
				</thead>
				<tbody>
					{#each game_data.questions[parseInt(question_index)].answers as answer}
						<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
							<td
								class="py-4 px-6 text-sm font-medium text-gray-900 whitespace-nowrap dark:text-white"
							>
								{answer.answer}
							</td>
							<td
								class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
							>
								{data_store[answer.answer]}
							</td>
							<td
								class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
							>
								{#if answer.right}
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
</div>
