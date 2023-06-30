<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let data: PageData;
</script>

<div class="w-full">
	<div class="flex justify-center w-full">
		<div class="w-11/12 m-auto">
			{#if data.results.length === 0}
				<p class="text-center text-3xl mt-8">{$t('results_page.no_results_so_far')}</p>
			{:else}
				<table class="w-full">
					<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
						<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
							>{$t('results_page.quiz_title')}
						</th>
						<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
							>{$t('results_page.date_played')}
						</th>
						<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
							>{$t('results_page.player_count')}
						</th>
						<th class="mx-auto p-1">{$t('words.note')}</th>
					</tr>
					{#each data.results as result}
						<tr class="text-left">
							<td class="border-r dark:border-gray-500 p-1 border-gray-300"
								><a href="/results/{result.id}" class="underline text-lg"
									>{result.title}</a
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
			{/if}
		</div>
	</div>
</div>
