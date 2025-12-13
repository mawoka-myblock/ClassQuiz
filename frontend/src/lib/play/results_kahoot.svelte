<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	interface Props {
		scores: any;
		question_results: Array<{
			username: string;
			answer: string;
			right: boolean;
			time_taken: number;
			score: number;
		}>;
		username: any;
	}

	let { scores = $bindable(), question_results, username }: Props = $props();
	let score_by_username = $state({});

	if (JSON.stringify(scores) === '{}') {
		for (const i of question_results) {
			scores[i.username] = 0;
		}
	}
	for (const i of question_results) {
		score_by_username[i.username] = i.score;
	}
	for (const username of Object.keys(score_by_username)) {
		scores[username] = (score_by_username[username] ?? 0) + (scores[username] ?? 0);
	}
	scores = scores;
	let sorted_scores = $derived(sortObjectbyValue(scores));
</script>

<div>
	<div class="flex justify-center h-screen">
		<div class="m-auto flex flex-col">
			<p class="p-4 bg-black/40 rounded-lg text-2xl">
				+{score_by_username[username] ?? '0'}
			</p>
			<p>Total score: {sorted_scores[username] ?? '0'}</p>
		</div>
	</div>
</div>
