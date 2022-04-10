<script lang="ts">
	import type { Answer, QuizData } from '../../app';

	export let results: Array<Answer>;
	export let game_data: QuizData;
	export let question_index: string;
	let data_store = {};

	const question = game_data.questions[parseInt(question_index)].answers;
	for (let i = 0; i < question.length; i++) {
		console.log(question[i].answer, 'HI!!!');
		data_store[question[i].answer] = 0;
	}
	console.log(data_store);

	for (let i = 0; i < results.length; i++) {
		console.log(results[i].answer);
		data_store[results[i].answer] += 1;
	}

	console.log(data_store);
</script>

<!-- Show the results from the results object -->
<!-- Language: SvelteHTML -->
<!-- Path: frontend/src/lib/play/show_results.svelte -->

<div>
	<h2>Results</h2>
	<div class="flex flex-col mx-auto">
		<div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
			<div class="inline-block py-2 min-w-full sm:px-6 lg:px-8">
				<div class="overflow-hidden shadow-md sm:rounded-lg">
					<table class="min-w-full">
						<thead class="bg-gray-50 dark:bg-gray-700">
							<tr>
								<th
									scope="col"
									class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
								>
									Answer
								</th>
								<th
									scope="col"
									class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
								>
									Count
								</th>
								<th
									scope="col"
									class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
								>
									Right
								</th>
							</tr>
						</thead>
						<tbody>
							<!-- Product 1 -->
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
								</tr>{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>
