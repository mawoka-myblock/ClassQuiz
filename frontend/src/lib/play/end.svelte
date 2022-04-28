<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';

	export let quiz_data: QuizData;
	export let final_results: Array<null> | Array<Array<PlayerAnswer>>;

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	const getWinnersSorted = () => {
		let winners = {};
		let q_count = quiz_data.questions.length;
		for (let i = 0; i < q_count; i++) {
			let q_res = final_results[i];
			if (q_res === null) {
				continue;
			}
			for (let j = 0; j < q_res.length; j++) {
				let res = q_res[j];
				if (res['right']) {
					if (winners[res['username']] === undefined) {
						winners[res['username']] = 0;
					}
					winners[res['username']] += 1;
				}
			}
		}

		function sortObjectbyValue(obj) {
			const asc = false;
			const ret = {};
			Object.keys(obj)
				.sort((a, b) => obj[asc ? a : b] - obj[asc ? b : a])
				.forEach((s) => (ret[s] = obj[s]));
			return ret;
		}

		return sortObjectbyValue(winners);
	};
	let winners = getWinnersSorted();
	let winners_arr = Object.keys(winners);
	console.log(winners);
</script>

<div>
	<h1 class="mx-auto text-center text-6xl mt-8">That's it! This was the quiz.</h1>

	<div class="flex mx-auto w-fit flex-col pt-8 gap-2">
		<div>
			<p class="text-3xl text-center">
				1st Place: <span class="underline">{winners_arr[0]}</span>
				<span>with {winners[winners_arr[0]]} out of {quiz_data.questions.length}</span>
			</p>
		</div>
		{#if winners_arr.length >= 2}
			<div>
				<p class="text-2xl text-center">
					2nd Place: <span class="underline">{winners_arr[1]}</span>
					<span>with {winners[winners_arr[1]]} out of {quiz_data.questions.length}</span>
				</p>
			</div>
		{/if}
		{#if winners_arr.length >= 3}
			<div>
				<p class="text-xl text-center">
					3nd Place: <span class="underline">{winners_arr[3]}</span><span
						>With {winners[winners_arr[3]]}</span
					>
				</p>
			</div>
		{/if}
	</div>
</div>
