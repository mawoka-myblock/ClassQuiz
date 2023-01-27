<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import { navbarVisible, signedIn } from '$lib/stores';
	import Spinner from '$lib/Spinner.svelte';
	import Fuse from 'fuse.js';
	import BrownButton from '$lib/components/buttons/brown.svelte';

	interface QuizData {
		id: string;
		public: boolean;
		title: string;
		description: string;
		created_at: string;
		updated_at: string;
		user_id: string;
		questions: Question[];
	}

	let search_term = '';
	signedIn.set(true);
	navbarVisible.set(true);
	const { t } = getLocalization();

	let quizzes_to_show = [];
	let quizzes: Array<any>;
	let fuse;
	/*	const minisearch = new MiniSearch({
				fields: ['title', 'description'],
				idField: 'id',
				storeFields: ['id']
			})*/

	let id_to_position_map = {};

	const getData = async (): Promise<Array<QuizData>> => {
		const res = await fetch('/api/v1/quiz/list');
		quizzes_to_show = await res.json();
		fuse = new Fuse(quizzes_to_show, {
			keys: ['title', 'description', 'questions.question'],
			findAllMatches: true
		});
		quizzes = quizzes_to_show;
		for (let i = 0; i < quizzes.length; i++) {
			id_to_position_map[quizzes[i].id] = i;
		}
		return quizzes_to_show;
	};

	let suggestions = [];

	const search = () => {
		if (search_term === '') {
			quizzes_to_show = [];
			quizzes_to_show = quizzes;
			quizzes_to_show = quizzes_to_show;
		} else {
			const res = fuse.search(search_term);
			console.log(res, 'search_res');
			quizzes_to_show = [];
			for (const quiz_data of res) {
				quizzes_to_show.push(quiz_data.item);
			}

			quizzes_to_show = quizzes_to_show;
		}
	};
	$: {
		search_term;
		console.log(search_term);
		search();
	}
</script>

<svelte:head>
	<title>ClassQuiz - Dashboard</title>
</svelte:head>

<div class="min-h-screen flex flex-col">
	{#await getData()}
		<svg class="h-8 w-8 animate-spin mx-auto my-20" viewBox="3 3 18 18">
			<path
				class="fill-black"
				d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
			/>
			<path
				class="fill-blue-100"
				d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"
			/>
		</svg>
	{:then quizzes}
		<div class="flex flex-col w-fit mx-auto">
			<!--		<button
					class='px-4 py-2 font-medium tracking-wide text-gray-500 whitespace-nowrap dark:text-gray-400 capitalize transition-colors dark:bg-gray-700 duration-200 transform bg-[#B07156] rounded-md hover:bg-green-600 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-80'>
					Primary
				</button>-->
			<div class="w-full grid grid-cols-4 gap-2">
				<BrownButton href="/create">{$t('words.create')}</BrownButton>
				<BrownButton href="/import">{$t('words.import')}</BrownButton>
				<BrownButton href="/api/v1/users/logout">{$t('words.logout')}</BrownButton>
				<BrownButton href="/account/settings">
					{$t('words.settings')}
				</BrownButton>
			</div>
			{#if quizzes.length !== 0}
				{#await import('$lib/dashboard/main_slider.svelte')}
					<Spinner />
				{:then c}
					<div class="flex justify-center pt-4 w-full">
						<div>
							<div>
								<input
									bind:value={search_term}
									class="p-2 rounded-lg outline-none text-center w-96 dark:bg-gray-700"
									placeholder={$t('dashboard.search_for_own_quizzes')}
								/>
								<button
									on:click={() => {
										search_term = '';
										quizzes_to_show = quizzes;
										suggestions = [];
									}}
								>
									<svg
										class="h-8 inline-block"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M6 18L18 6M6 6l12 12"
										/>
									</svg>
								</button>
							</div>
						</div>
					</div>
					<svelte:component this={c.default} bind:quizzes={quizzes_to_show} />
				{/await}
			{:else}
				<p>
					{$t('overview_page.no_quizzes')}
				</p>
			{/if}
		</div>
	{:catch err}
		<p>{err}</p>
	{/await}
</div>
<Footer />
