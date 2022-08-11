<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script context="module" lang="ts">
	export async function load({ session }) {
		if (!session.authenticated) {
			return {
				status: 302,
				redirect: '/account/login?returnTo=/dashboard'
			};
		}
		return {
			props: {
				email: session.email
			}
		};
	}
</script>

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { DateTime } from 'luxon';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import { alertModal, navbarVisible, signedIn } from '$lib/stores';

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

	signedIn.set(true);
	navbarVisible.set(true);
	const { t } = getLocalization();

	const getData = async (): Promise<Array<QuizData>> => {
		const res = await fetch('/api/v1/quiz/list');
		return await res.json();
	};

	const formatDate = (date: string): string => {
		const dt = DateTime.fromISO(date);
		return dt.toLocaleString(DateTime.DATETIME_MED);
	};

	const startGame = async (id: string): Promise<void> => {
		console.log('start game', id);
		let res;
		if (window.confirm('Do you want to enable the captcha for players?')) {
			res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=True`, {
				method: 'POST'
			});
		} else {
			res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=False`, {
				method: 'POST'
			});
		}

		if (res.status !== 200) {
			alertModal.set({
				open: true,
				title: 'Start failed',
				body: `Failed to start game, ${await res.text()}`
			});
			alertModal.subscribe((_) => {
				window.location.assign('/account/login?returnTo=/dashboard');
			});
		}
		const data = await res.json();
		// eslint-disable-next-line no-undef
		plausible('Started Game', { props: { quiz_id: id } });
		window.location.assign(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
	};

	const deleteQuiz = async (to_delete: string) => {
		await fetch(`/api/v1/quiz/delete/${to_delete}`, {
			method: 'DELETE'
		});
		window.location.reload();
	};
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
					class='px-4 py-2 font-medium tracking-wide text-gray-500 whitespace-nowrap dark:text-gray-400 capitalize transition-colors dark:bg-gray-700 duration-200 transform bg-gray-50 rounded-md hover:bg-green-600 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-80'>
					Primary
				</button>-->
			<div class="w-full grid grid-cols-4 gap-2">
				<a
					href="/create"
					class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					>{$t('words.create')}
				</a>
				<a
					href="/import"
					class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					>{$t('words.import')}
				</a>
				<a
					href="/api/v1/users/logout"
					class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
					>{$t('words.logout')}
				</a>
				<a
					href="/account/settings"
					class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
				>
					{$t('words.settings')}
				</a>
			</div>
			{#if quizzes.length !== 0}
				<div class="overflow-x-auto sm:-mx-8 lg:-mx-8">
					<div class="inline-block py-2 min-w-full sm:px-6 lg:px-8">
						<div class="overflow-hidden shadow-md sm:rounded-lg">
							<table class="min-w-full">
								<thead class="bg-gray-50 dark:bg-gray-700">
									<tr>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
										>
											{$t('words.title')}
										</th>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 dark:text-gray-400 uppercase"
										>
											{$t('overview_page.created_at')}
										</th>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
										>
											{$t('overview_page.question_count')}
										</th>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
										>
											{$t('words.play')}
										</th>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
										>
											{$t('words.edit')}
										</th>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
										>
											{$t('words.delete')}
										</th>
										<th
											scope="col"
											class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
										>
											{$t('words.public')}
										</th>
									</tr>
								</thead>
								<tbody>
									{#each quizzes as quiz}
										<tr
											class="bg-white border-b dark:bg-gray-800 dark:border-gray-700"
										>
											<td
												class="py-4 px-6 text-sm font-medium text-gray-900 whitespace-nowrap dark:text-white"
											>
												{quiz.title}
											</td>
											<td
												class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
											>
												{formatDate(quiz.created_at)}
											</td>
											<td
												class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
											>
												{quiz.questions.length}
											</td>
											<td
												class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
											>
												<button
													on:click={() => {
														startGame(quiz.id);
													}}
													class="border border-green-600"
												>
													{$t('words.start')}
												</button>
											</td>
											<td
												class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
											>
												<a
													href="/edit?quiz_id={quiz.id}"
													class="border border-yellow-600"
													>{$t('words.edit')}</a
												>
											</td>
											<td
												class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
											>
												<button
													on:click={() => {
														deleteQuiz(quiz.id);
													}}
													class="border border-red-600"
												>
													{$t('words.delete')}
												</button>
											</td>
											<td
												class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
											>
												{#if quiz.public}
													✅
												{:else}
													❌
												{/if}
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				</div>
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
