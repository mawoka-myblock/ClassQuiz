<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	export let scores;

	export let question_results: Array<{
		username: string;
		answer: string;
		right: boolean;
		time_taken: number;
		score: number;
	}>;

	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	export let username;
	let score_by_username = {};

	if (JSON.stringify(scores) === '{}') {
		for (const i of question_results) {
			scores[i.username] = 0;
		}
	}

	for (const i of question_results) {
		score_by_username[i.username] = i.score;
	}

	$: scores = sortObjectbyValue(scores);

	for (const i of Object.keys(scores)) {
		scores[i] = score_by_username[i] + scores[i];
	}
</script>

<div>
	<div class="flex justify-center h-screen">
		<div class="m-auto flex flex-col">
			<p class="p-4 bg-black bg-opacity-40 rounded-lg text-2xl">
				+{score_by_username[username]}
			</p>
			<p>Total score: {scores[username]}</p>
		</div>
	</div>
</div>
