<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let question_results: Array<{
		username: string;
		answer: string;
		right: boolean;
		time_taken: number;
		score: number;
		total_score: number;
	}>;

	export let username;
	let score_by_username = {};
	let total_score_by_username = {};

	$: console.log(score_by_username, total_score_by_username, 'dieter');
	for (const i of question_results) {
		score_by_username[i.username] = i.score;
		total_score_by_username[i.username] = i.total_score;
	}
</script>

<div>
	<div class="flex justify-center h-screen">
		<div class="m-auto flex flex-col">
			<p class="p-4 bg-black bg-opacity-40 rounded-lg text-2xl">
				+{score_by_username[username] ?? '0'}
			</p>
			<p>Total score: {total_score_by_username[username] ?? '0'}</p>
		</div>
	</div>
</div>
