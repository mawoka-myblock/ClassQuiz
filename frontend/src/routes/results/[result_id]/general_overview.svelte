<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Question } from '$lib/quiz_types';

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

<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<div class="w-full">
	<div class="flex justify-center w-full">
		<p class="text-3xl w-5/6 text-center">
			The quiz with the title '<strong>{title}</strong>' was played on
			<strong>{new Date(timestamp).toLocaleString()}</strong>
			with <strong>{usernames.length}</strong> players. The players achieved an average score
			of <strong>{get_average_final_score()}</strong>.
		</p>
	</div>
</div>

<style>
	underline {
		text-decoration: underline;
	}
</style>
