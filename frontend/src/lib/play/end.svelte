<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let quiz_data: QuizData;
	export let final_results: Array<null> | Array<Array<PlayerAnswer>>;

	interface PlayerAnswer {
		username: string;
		answer: string;
		right: string;
	}

	let data_available = false;
	let winners_arr;

	const getWinnersSorted = () => {
		let winners = {};
		let q_count = quiz_data.questions.length;
		console.log(
			JSON.stringify(final_results),
			JSON.stringify(final_results) === '{}',
			'HI!!!!!',
			JSON.stringify(final_results) === JSON.stringify({})
		);

		function sortObjectbyValue(obj) {
			const ret = {};
			Object.keys(obj)
				.sort((a, b) => obj[b] - obj[a])
				.forEach((s) => (ret[s] = obj[s]));
			return ret;
		}

		try {
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

			let close_to_res = sortObjectbyValue(winners);
			winners_arr = [];
			for (const i in close_to_res) {
				winners_arr.push([i, close_to_res[i]]);
			}

			winners_arr = winners_arr.sort(function (a, b) {
				return b[1] - a[1];
			});
			data_available = true;
			return close_to_res;
		} catch (e) {
			data_available = false;
		}
	};
	let winners = getWinnersSorted();
	$: {
		console.log(winners, winners_arr);
	}
</script>

<div>
	<h1 class="mx-auto text-center text-6xl mt-8">{$t('play_page.end_sentence')}</h1>
	{#if data_available}
		{#if winners_arr[0][0] === undefined}
			<div class="flex justify-center">
				<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
			</div>
		{:else}
			<div class="flex mx-auto w-fit flex-col pt-8 gap-2">
				<div>
					<p class="text-3xl text-center">
						{$t('play_page.1st_place')}:
						<span class="underline">{winners_arr[0][0]}</span>
						<span
							>{$t('play_page.with_out_of', {
								correct_questions: winners_arr[0][1] ?? 0,
								total_question_count: quiz_data.questions.length
							})}</span
						>
					</p>
				</div>
				{#if winners_arr.length >= 2 && winners_arr[1][0] !== undefined}
					<div>
						<p class="text-2xl text-center">
							{$t('play_page.2nd_place')}:
							<span class="underline">{winners_arr[1][0]}</span>
							<span
								>{$t('play_page.with_out_of', {
									correct_questions: winners_arr[1][1] ?? 0,
									total_question_count: quiz_data.questions.length
								})}</span
							>
						</p>
					</div>
				{/if}
				{#if winners_arr.length >= 3 && winners_arr[2][0] !== undefined}
					<div>
						<p class="text-xl text-center">
							{$t('play_page.3rd place')}:
							<span class="underline">{winners_arr[2][0]}</span>
							<span>
								{$t('play_page.with_out_of', {
									correct_questions: winners_arr[2][1] ?? 0,
									total_question_count: quiz_data.questions.length
								})}
							</span>
						</p>
					</div>
				{/if}
			</div>
		{/if}
	{:else}
		<div class="flex justify-center">
			<h1 class="text-3xl">{$t('admin_page.no_answers')}</h1>
		</div>
	{/if}
</div>
