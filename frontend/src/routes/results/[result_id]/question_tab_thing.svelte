<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	export let question;

	interface Answer {
		username: string;
		answer: string;
		right: boolean;
		time_taken: number;
		score: number;
	}

	export let answers: Answer[];
	console.log(question);

	const get_answer_count_for_answer = (answer: string): number => {
		let count = 0;
		for (const a of answers) {
			if (a.answer === answer) {
				count++;
			}
		}
		return count;
	};
</script>

<div class="flex justify-center">
	<div class="bg-white p-2 -z-10 w-10/12 rounded">
		<div class="flex flex-col">
			{#each question.answers as answer}
				<div class="grid grid-cols-4">
					<p>{answer.answer}</p>
					<div
						class="col-span-3 flex w-full border-l border-gray-300 px-1 dark:border-gray-500"
					>
						<div class="my-auto w-full mr-1">
							<span
								class="h-1 block bg-green-600 my-auto"
								style="width: {(get_answer_count_for_answer(answer.answer) /
									answers.length) *
									100}%"
							/>
						</div>
						<p>{get_answer_count_for_answer(answer.answer)}</p>
						<p class="ml-1">
							{#if answer.right}✅{:else}❌{/if}
						</p>
					</div>
				</div>
			{/each}
		</div>
		<div class="mt-4">
			<table class="w-full text-left">
				<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Player Name</th
					>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300">Score</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Time Taken</th
					>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300">Answer</th
					>
					<th class="p-1">Correct?</th>
				</tr>
				{#each answers as answer}
					<tr>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{answer.username}</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{answer.score}</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{(answer.time_taken / 1000).toFixed(3)}s</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{answer.answer}</td
						>
						<td class="p-1"
							>{#if answer.right}✅{:else}❌{/if}</td
						>
					</tr>
				{/each}
			</table>
		</div>
	</div>
</div>
