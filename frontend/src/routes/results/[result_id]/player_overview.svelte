<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	interface Props {
		scores: {
			[key: string]: string;
		};
		custom_field: {
			[key: string]: string;
		};
		answers: { [key: string]: any }[];
	}

	let { scores, custom_field, answers }: Props = $props();

	let usernames = Object.keys(scores);
	const correctCounts = {};
	answers.forEach((questionAnswers) => {
		questionAnswers.forEach((answer) => {
			const user = answer.username;
			if (!correctCounts[user]) {
				correctCounts[user] = 0;
			}
			if (answer.right) {
				correctCounts[user] += 1;
			}
		});
	});
</script>

<div class="w-full">
	<div class="flex justify-center w-full">
		<table class="w-11/12 m-auto">
			<thead>
				<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('result_page.player_name')}
					</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('result_page.player_correct_questions')}
					</th>
					<th class="p-1 mx-auto">{$t('result_page.player_score')}</th>
					{#if Object.keys(custom_field).length !== 0}
						<th class="border-l dark:border-gray-500 p-1 mx-auto border-gray-300"
							>{$t('result_page.custom_field')}
						</th>
					{/if}
				</tr>
			</thead>
			<tbody>
				{#each usernames as uname}
					<tr class="text-left">
						<td class="border-r dark:border-gray-500 p-1 border-gray-300">{uname}</td>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{correctCounts[uname]}</td
						>
						<td class="p-1">{scores[uname]}</td>
						{#if custom_field[uname]}
							<td class="border-l dark:border-gray-500 p-1 border-gray-300"
								>{custom_field[uname]}</td
							>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
