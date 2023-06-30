<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let questions: Question[];
	export let answers: {
		username: string;
		answer: string;
		right: boolean;
		tike_taken: number;
		score: number;
	}[][];

	export let scores: {
		[key: string]: string;
	};
	export let title: string;
	export let timestamp: string;

	const usernames = Object.keys(scores);

	const get_average_final_score = () => {
		let score_data = 0;
		for (const username of usernames) {
			score_data += parseInt(scores[username]);
		}
		return score_data / usernames.length;
	};
</script>

<div class="w-full">
	<div class="flex justify-center w-full">
		<p class="text-3xl w-5/6 text-center">
			{$t('results_page.general_overview.sentence', {
				title,
				date: new Date(timestamp).toLocaleString(),
				player_count: usernames.length,
				average_score: get_average_final_score()
			})}
		</p>
	</div>
</div>

<style>
	underline {
		text-decoration: underline;
	}
</style>
