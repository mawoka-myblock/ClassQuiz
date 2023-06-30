<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let scores: {
		[key: string]: string;
	};
	export let custom_field: {
		[key: string]: string;
	};

	let usernames = Object.keys(scores);
	console.log(custom_field);
</script>

<div class="w-full">
	<div class="flex justify-center w-full">
		<table class="w-11/12 m-auto">
			<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
				<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
					>{$t('result_page.player_name')}
				</th>
				<th class="p-1 mx-auto">{$t('result_page.player_score')}</th>
				{#if Object.keys(custom_field).length !== 0}
					<th class="border-l dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('result_page.custom_field')}
					</th>
				{/if}
			</tr>
			{#each usernames as uname}
				<tr class="text-left">
					<td class="border-r dark:border-gray-500 p-1 border-gray-300">{uname}</td>
					<td class="p-1">{scores[uname]}</td>
					{#if custom_field[uname]}
						<td class="border-l dark:border-gray-500 p-1 border-gray-300"
							>{custom_field[uname]}</td
						>
					{/if}
				</tr>
			{/each}
		</table>
	</div>
</div>
