<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';

	export let quiz: QuizData;
	export let answers: {
		username: string;
		answer: string;
		right: boolean;
		tike_taken: number;
		score: number;
	}[];
</script>
