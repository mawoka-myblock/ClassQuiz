<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import DownloadQuiz from '$lib/components/DownloadQuiz.svelte';
	import type { QuizData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import { navbarVisible, signedIn } from '$lib/stores';
	import CommandpaletteNotice from '$lib/components/popover/commandpalettenotice.svelte';
	// import Spinner from "$lib/Spinner.svelte";
	import Fuse from 'fuse.js';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import type { PageData } from './$types';
	import { fly } from 'svelte/transition';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';
	import Analytics from './Analytics.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { createTippy } from 'svelte-tippy';

	// import GrayButton from "$lib/components/buttons/gray.svelte";

	export let data: PageData;
	let search_term = '';
	let start_game = null;
	let download_id: string | null = null;
	signedIn.set(true);
	navbarVisible.set(true);
	const { t } = getLocalization();

	let items_to_show = [];
	let all_items: Array<any>;
	let fuse;
	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'bottom'
	});

	let id_to_position_map = {};

	const getData = async (): Promise<Array<QuizData>> => {
		items_to_show = [];
		for (let i = 0; i < data.quizzes.length; i++) {
			items_to_show.push({ ...data.quizzes[i], type: 'quiz' });
		}
		for (let i = 0; i < data.quiztivities.length; i++) {
			items_to_show.push({ ...data.quiztivities[i], type: 'quiztivity' });
		}
		fuse = new Fuse(items_to_show, {
			keys: ['title', 'description', 'questions.title'],
			findAllMatches: true
		});
		all_items = items_to_show;
		for (let i = 0; i < all_items.length; i++) {
			id_to_position_map[all_items[i].id] = i;
		}
		return all_items;
	};

	const search = () => {
		if (search_term === '') {
			items_to_show = all_items;
		} else {
			const res = fuse.search(search_term);
			console.log(res, 'search_res');
			items_to_show = [];
			for (const quiz_data of res) {
				items_to_show.push(quiz_data.item);
			}

			items_to_show = items_to_show;
		}
	};
	$: {
		search_term;
		search();
	}

	const deleteQuiz = async (to_delete: string, type: 'quiz' | 'quiztivity') => {
		if (!confirm('Do you really want to delete this quiz?')) {
			return;
		}
		if (type === 'quiz') {
			await fetch(`/api/v1/quiz/delete/${to_delete}`, {
				method: 'DELETE'
			});
		} else {
			await fetch(`/api/v1/quiztivity/${to_delete}`, {
				method: 'DELETE'
			});
		}
		window.location.reload();
	};
	let create_button_clicked = false;

	let analytics_quiz_selected: undefined | QuizData = undefined;
</script>

<svelte:head>
	<title>ClassQuiz - Dashboard</title>
</svelte:head>
<Analytics bind:quiz={analytics_quiz_selected} />
<CommandpaletteNotice />
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
		<div class="flex flex-col w-full mx-auto">
			<!--		<button
                    class='px-4 py-2 font-medium tracking-wide text-gray-500 whitespace-nowrap dark:text-gray-400 capitalize transition-colors dark:bg-gray-700 duration-200 transform bg-[#B07156] rounded-md hover:bg-green-600 focus:outline-none focus:ring focus:ring-blue-300 focus:ring-opacity-80'>
                    Primary
                </button>-->
			<div class="w-full grid lg:grid-cols-4 gap-2 grid-cols-2 px-4">
				{#if create_button_clicked}
					<div
						class="flex gap-2"
						transition:fly={{ y: 10 }}
						use:tippy={{ content: 'Unsure? Choose "Quiz".' }}
					>
						<BrownButton href="/create">{$t('words.quiz')}</BrownButton>
						<BrownButton href="/quiztivity/create">{$t('words.quiztivity')}</BrownButton
						>
					</div>
				{:else}
					<BrownButton
						on:click={() => {
							create_button_clicked = true;
						}}>{$t('words.create')}</BrownButton
					>
				{/if}
				<BrownButton href="/import">{$t('words.import')}</BrownButton>
				<BrownButton href="/results">{$t('words.results')}</BrownButton>
				<div class="flex gap-2">
					<BrownButton href="/edit/files">{$t('words.files_library')}</BrownButton>
					<BrownButton href="/account/settings">
						{$t('words.settings')}
					</BrownButton>
				</div>
			</div>
			{#if quizzes.length !== 0}
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
									items_to_show = all_items;
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
				<div class="flex flex-col gap-4 mt-4 px-2">
					{#each items_to_show as quiz}
						<div
							class="grid grid-cols-2 lg:grid-cols-3 w-full rounded border-[#B07156] border-2 p-2 h-[20vh] overflow-hidden max-h-[20vh]"
						>
							<div class="hidden lg:flex w-auto h-full items-center relative">
								{#if quiz.cover_image}
									<!--									<img
										src="/api/v1/storage/download/{quiz.cover_image}"
										alt="user provided"
										loading="lazy"
										class="shrink-0 max-w-full max-h-full absolute rounded"
									/>-->
									<MediaComponent
										src={quiz.cover_image}
										css_classes="shrink-0 max-w-full max-h-full absolute rounded"
									/>
								{/if}
							</div>
							<div class="my-auto mx-auto max-h-full overflow-hidden">
								<p class="text-xl text-center">{@html quiz.title}</p>
								<p class="text-sm text-center text-clip overflow-hidden">
									{@html quiz.description ?? ''}
								</p>
							</div>
							<div
								class="grid grid-rows-2 ml-auto gap-2 w-fit self-end my-auto"
								class:grid-cols-3={quiz.type === 'quiz'}
								class:grid-cols-2={quiz.type !== 'quiztivity'}
							>
								<BrownButton
									flex={true}
									disabled={!quiz.public}
									href="/view/{quiz.id}"
								>
									<!-- heroicons/legacy-outline/Eye -->
									<svg
										class="w-5 h-5"
										aria-hidden="true"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
										<path
											d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								</BrownButton>
								<BrownButton
									flex={true}
									on:click={() => (analytics_quiz_selected = quiz)}
								>
									<!-- heroicons/legacy-outline/ChartBar -->
									<svg
										class="w-5 h-5"
										aria-hidden="true"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								</BrownButton>
								<BrownButton
									href={quiz.type === 'quiz'
										? `/edit?quiz_id=${quiz.id}`
										: `/quiztivity/edit?id=${quiz.id}`}
									flex={true}
								>
									<!-- heroicons/legacy-outline/Pencil -->
									<svg
										class="w-5 h-5"
										aria-hidden="true"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								</BrownButton>
								{#if quiz.type === 'quiz'}
									<BrownButton
										on:click={() => {
											start_game = quiz.id;
										}}
										flex={true}
									>
										<!-- heroicons/legacy-outline/Play -->
										<svg
											class="w-5 h-5"
											aria-hidden="true"
											fill="none"
											stroke="currentColor"
											stroke-width="2"
											viewBox="0 0 24 24"
											xmlns="http://www.w3.org/2000/svg"
										>
											<path
												d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
												stroke-linecap="round"
												stroke-linejoin="round"
											/>
											<path
												d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
												stroke-linecap="round"
												stroke-linejoin="round"
											/>
										</svg>
									</BrownButton>
								{:else}
									<BrownButton href="/quiztivity/play?id={quiz.id}" flex={true}>
										<!-- heroicons/legacy-outline/Play -->
										<svg
											class="w-5 h-5"
											aria-hidden="true"
											fill="none"
											stroke="currentColor"
											stroke-width="2"
											viewBox="0 0 24 24"
											xmlns="http://www.w3.org/2000/svg"
										>
											<path
												d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
												stroke-linecap="round"
												stroke-linejoin="round"
											/>
											<path
												d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
												stroke-linecap="round"
												stroke-linejoin="round"
											/>
										</svg>
									</BrownButton>
								{/if}

								<BrownButton
									on:click={() => {
										deleteQuiz(quiz.id, quiz.type);
									}}
									flex={true}
								>
									<!-- heroicons/trash -->
									<svg
										class="w-5 h-5"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
										/>
									</svg>
								</BrownButton>
								<BrownButton
									on:click={() => (download_id = quiz.id)}
									flex={true}
									disabled={quiz.type !== 'quiz'}
									><!-- heroicons/download -->
									<svg
										class="w-5 h-5"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
										/>
									</svg>
								</BrownButton>
							</div>
						</div>
					{/each}
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
{#if start_game !== null}
	<StartGamePopup bind:quiz_id={start_game} />
{/if}
<DownloadQuiz bind:quiz_id={download_id} />
