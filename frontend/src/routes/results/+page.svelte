<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<div class="w-full">
	<div class="flex justify-center w-full">
		<div class="w-11/12 m-auto">
			<table class="w-full">
				<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Quiz Title
					</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Date Played
					</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Player count
					</th>
					<th class="mx-auto p-1">Note</th>
				</tr>
				{#each data.results as result}
					<tr class="text-left">
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							><a href="/results/{result.id}" class="underline text-lg"
								>{result.quiz.title}</a
							></td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{new Date(result.timestamp).toLocaleString()}</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{Object.keys(result.player_scores).length}</td
						>
						<td class:p-1={result.note}>
							{#if result.note}
								{result.note}
							{/if}
						</td>
					</tr>
				{/each}
			</table>
		</div>
	</div>
</div>
