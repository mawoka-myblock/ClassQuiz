<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { run } from 'svelte/legacy';



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

	run(() => {
		console.log(score_by_username, scores, 'dieter');
	});
	for (const i of question_results) {
		score_by_username[i.username] = i.score;
	}

	run(() => {
		scores = sortObjectbyValue(scores);
	});

	const do_sth = () => {
		for (const i of Object.keys(score_by_username)) {
			scores[i] = (score_by_username[i] ?? 0) + (scores[i] ?? 0);
		}
		scores = scores;
	};

	do_sth();
</script>

<div>
	<div class="flex justify-center h-screen">
		<div class="m-auto flex flex-col">
			<p class="p-4 bg-black/40 rounded-lg text-2xl">
				+{score_by_username[username] ?? '0'}
			</p>
			<p>Total score: {scores[username] ?? '0'}</p>
		</div>
	</div>
</div>
