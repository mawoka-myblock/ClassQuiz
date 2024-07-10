<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';
	import WebPOpenGraph from '$lib/assets/landing/opengraph-home.webp';
	import JpgOpenGraph from '$lib/assets/landing/opengraph-home.jpg';
	import Newsletter from '$lib/landing/newsletter.svelte';
	import { fly, fade } from 'svelte/transition';

	/*	import LandingPromo from '$lib/landing/landing-promo.svelte';*/

	import FindScreenshot from '$lib/assets/landing_new/find.webp';
	import ImportScreenshot from '$lib/assets/landing_new/import.webp';
	import EditScreenshot from '$lib/assets/landing_new/edit.webp';
	import SelectScreenshot from '$lib/assets/landing_new/select.webp';
	import ResultScreenshot from '$lib/assets/landing_new/result.webp';
	import WinnersScreenshot from '$lib/assets/landing_new/winners.webp';
	import { onMount } from 'svelte';

	const { t } = getLocalization();

	navbarVisible.set(true);

	/*	interface StatsData {
		quiz_count: number;
		user_count: number;
	}*/

	/*	const getStats = async (): Promise<StatsData> => {
			const response = await fetch('/api/v1/stats/combined');
			return await response.json();
		};*/
	let newsletterModalOpen;
	onMount(() => {
		const ls = localStorage.getItem('newsletter');
		newsletterModalOpen = ls === null;
	});

	// eslint-disable-next-line no-unused-vars
	enum SelectedCreateThing {
		// eslint-disable-next-line no-unused-vars
		Create,
		// eslint-disable-next-line no-unused-vars
		Find,
		// eslint-disable-next-line no-unused-vars
		Import
	}

	// eslint-disable-next-line no-unused-vars
	enum SelectedPlayThing {
		// eslint-disable-next-line no-unused-vars
		Select,
		// eslint-disable-next-line no-unused-vars
		Results,
		// eslint-disable-next-line no-unused-vars
		Winners
	}

	let selected_create_thing = SelectedCreateThing.Create;
	let selected_play_thing = SelectedPlayThing.Select;

	/*	<li>No;
		Tracking < /li>
		< li > Self - hostable < /li>
		< li > German;
		Server < /li>
		< li > user - friendly < /li>
		< li > Completely;
		free < /li>
		< li > Quiz - results;
		are;
		downloadable < /li>;*/

	const classquiz_reasons = [
		{
			headline: $t('index_page.no_player_limit'),
			content: $t('index_page.no_player_limit_content')
		},
		{
			headline: $t('index_page.no_tracking'),
			content: $t('index_page.no_tracking_content')
		},
		{
			headline: $t('index_page.self_hostable'),
			content: $t('index_page.self_hostable_content')
		},
		{
			headline: $t('index_page.german_server'),
			content: $t('index_page.german_server_content')
		},
		{
			headline: $t('index_page.user_friendly'),
			content: $t('index_page.user_friendly_content')
		},
		{
			headline: $t('index_page.completely_free'),
			content: $t('index_page.completely_free_content')
		},
		{
			headline: $t('index_page.quiz_results_downloadable'),
			content: $t('index_page.quiz_results_downloadable_content')
		},
		{
			headline: $t('index_page.multilingual'),
			content: $t('index_page.multilingual_content')
		},
		{
			headline: $t('index_page.dark_mode'),
			content: $t('index_page.dark_mode_content')
		},
		{
			headline: $t('index_page.download_quizzes'),
			content: $t('index_page.download_quizzes_content')
		},
		{
			headline: $t('index_page.community_driven'),
			content: $t('index_page.community_driven_content')
		}
	];
	let selected_classquiz_reason = 0;
</script>

<svelte:head>
	<title>ClassQuiz - {$t('index_page.meta.title')}</title>
	<meta name="description" content={$t('index_page.meta.description')} />
	<title>ClassQuiz - Home</title>
	<meta
		name="description"
		content="ClassQuiz is a quiz-application like KAHOOT!, but open-source. You can create quizzes and play them remotely with other people."
	/>

	<meta property="og:url" content="https://classquiz.de/" />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="ClassQuiz - {$t('index_page.meta.title')}" />
	<meta
		property="og:description"
		content="ClassQuiz is a quiz-application like KAHOOT!, but open-source. You can create quizzes and play them remotely with other people."
	/>
	<meta property="og:image" content={JpgOpenGraph} />

	<meta name="twitter:card" content="summary_large_image" />
	<meta property="twitter:domain" content="classquiz.de" />
	<meta property="twitter:url" content="https://classquiz.de/" />
	<meta name="twitter:title" content="ClassQuiz - {$t('index_page.meta.title')}" />
	<meta
		name="twitter:description"
		content="ClassQuiz is a quiz-application like KAHOOT!, but open-source. You can create quizzes and play them remotely with other people."
	/>
	<meta name="twitter:image" content={WebPOpenGraph} />
</svelte:head>

<!--<div class="min-h-screen flex flex-col">
	<section class="pb-40">
		<div class="pt-12 text-center">
			<h1 class="sm:text-8xl text-6xl mt-6 marck-script">ClassQuiz</h1>
			<p class="text-xl mt-4">{$t('index_page.slogan')}</p>
		</div>
	</section>

	<section id="features" class="mt-8">
		<div class="text-center snap-y">
			<h1 class="sm:text-6xl text-4xl">{$t('words.features')}</h1>
			<p class="text-xl pt-4">
				{$t('index_page.features_description.1')}
				<br />
				{$t('index_page.features_description.2')}
				<br />
				{$t('index_page.features_description.3')}
			</p>
		</div>
	</section>
	<section class="py-8">
		<h1 class="sm:text-6xl text-4xl text-center break-words">
			{$t('words.screenshot', { count: 2 })}
		</h1>
		<div>
			<LandingPromo />
		</div>
	</section>

	<section>
		<h1 class="sm:text-6xl text-4xl text-center">Testimonials</h1>
		{#await import('$lib/landing/testimonials.svelte') then testimonials}
			<svelte:component this={testimonials.default} />
		{/await}
	</section>

	<section id="stats">
		<div class="text-center pb-20 pt-10 snap-y">
			<h1 class="sm:text-6xl text-4xl">{$t('words.stats')}</h1>
			<p class="text-xl pt-4">
				{#await getStats() then stats}
					{$t('index_page.stats', {
						user_count: stats.user_count,
						quiz_count: stats.quiz_count
					})}
				{/await}
			</p>
		</div>
	</section>
</div>-->
<div class="min-h-screen flex flex-col">
	<section class="pb-40">
		<div class="pt-12 text-center">
			<h1 class="sm:text-8xl text-6xl mt-6 marck-script">ClassQuiz</h1>
			<p class="text-xl mt-4">{$t('index_page.slogan')}</p>
		</div>
	</section>
	<section>
		<h2 class="text-center text-5xl mb-6">{$t('index_page.how_does_classquiz_work')}</h2>

		<div class="flex justify-center w-full">
			<h3 class="text-center text-3xl rounded-t-lg bg-opacity-40 bg-white py-2 px-6">
				{$t('index_page.get_a_quiz')}
			</h3>
		</div>
		<div
			class="grid grid-rows-2 lg:grid-rows-1 lg:grid-cols-2 bg-opacity-40 bg-white shadow-lg mb-12 lg:mx-12 mx-4 rounded-lg"
		>
			<div>
				<div class="p-2 rounded-lg">
					{#if selected_create_thing === SelectedCreateThing.Create}
						<img
							class="rounded-lg relative"
							src={EditScreenshot}
							in:fade
							alt="Screenshot of the import-page showing an URL to Kahoot! entered"
						/>
					{:else if selected_create_thing === SelectedCreateThing.Find}
						<img
							class="rounded-lg relative"
							src={FindScreenshot}
							in:fade
							alt="Screenshot of the search-page showing one found quiz for the term 'Country'"
						/>
					{:else if selected_create_thing === SelectedCreateThing.Import}
						<img
							class="rounded-lg relative"
							src={ImportScreenshot}
							in:fade
							alt="Screenshot of the import-page showing an URL to Kahoot! entered"
						/>
					{:else}
						<p>Shouldn't happen!</p>
					{/if}
				</div>
			</div>
			<div
				class="lg:border-l lg:border-l-black lg:border-t-0 border-t border-t-black flex lg:flex-col flex-row stretch"
			>
				<div
					class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
					on:click={() => {
						selected_create_thing = SelectedCreateThing.Create;
					}}
					on:keyup={() => {
						selected_create_thing = SelectedCreateThing.Create;
					}}
					class:shadow-2xl={selected_create_thing === SelectedCreateThing.Create}
					class:opacity-70={selected_create_thing !== SelectedCreateThing.Create}
				>
					<div
						class="rounded-lg w-fit p-1 bg-lime-500 hover:bg-lime-400 transition shadow-lg"
					>
						<svg
							aria-label="Pencil-Icon"
							class="w-8 h-8 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
							/>
						</svg>
					</div>
					<h5 class="text-xl w-fit dark:text-black">{$t('words.create')}</h5>
					<p class="dark:text-black">{$t('index_page.create_a_quiz_from_scratch')}</p>
				</div>
				<div
					class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
					on:click={() => {
						selected_create_thing = SelectedCreateThing.Find;
					}}
					on:keyup={() => {
						selected_create_thing = SelectedCreateThing.Find;
					}}
					class:shadow-2xl={selected_create_thing === SelectedCreateThing.Find}
					class:opacity-70={selected_create_thing !== SelectedCreateThing.Find}
				>
					<div
						class="rounded-lg w-fit p-1 bg-lime-500 hover:bg-lime-400 transition shadow-lg"
					>
						<svg
							class="w-8 h-8 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							aria-label="magnifying glass-Icon"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							/>
						</svg>
					</div>
					<h5 class="text-xl dark:text-black">{$t('words.find')}</h5>
					<p class="dark:text-black">{$t('index_page.find_or_explore')}</p>
				</div>
				<!--<div
					class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
					on:click={() => {
						selected_create_thing = SelectedCreateThing.Import;
					}}
					class:shadow-2xl={selected_create_thing === SelectedCreateThing.Import}
					class:opacity-70={selected_create_thing !== SelectedCreateThing.Import}
				>
					<div
						class="rounded-lg w-fit p-1 bg-lime-500 hover:bg-lime-400 transition shadow-lg"
					>
						<svg
							class="w-8 h-8 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							aria-label="Cloud with arrow pointing down"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
							/>
						</svg>
					</div>
					<h5 class="text-xl dark:text-black">{$t('words.import')}</h5>
					<p class="dark:text-black">
						{$t('index_page.import_quiz_from_kahoot_and_edit')}
					</p>
				</div>-->
			</div>
		</div>
	</section>

	<section class="mt-24">
		<div class="flex justify-center w-full">
			<h2 class="text-center text-3xl rounded-t-lg bg-opacity-40 bg-white py-2 px-6">
				{$t('index_page.play_quiz')}
			</h2>
		</div>

		<div
			class="grid grid-rows-2 lg:grid-rows-1 lg:grid-cols-2 bg-opacity-40 bg-white shadow-lg mb-12 lg:mx-12 mx-4 rounded-lg"
		>
			<div>
				<div class="p-2 rounded-lg">
					{#if selected_play_thing === SelectedPlayThing.Select}
						<img
							class="rounded-lg relative"
							src={SelectScreenshot}
							in:fade
							alt="Screenshot of the screen where an answer can be selected"
						/>
					{:else if selected_play_thing === SelectedPlayThing.Results}
						<img
							class="rounded-lg relative"
							src={ResultScreenshot}
							in:fade
							alt="Screenshot of the results with a table showing how many players chose which answer"
						/>
					{:else if selected_play_thing === SelectedPlayThing.Winners}
						<img
							class="rounded-lg relative"
							src={WinnersScreenshot}
							in:fade
							alt="Screenshot of the import-page showing an URL to Kahoot! entered"
						/>
					{:else}
						<p>Shouldn't happen!</p>
					{/if}
				</div>
			</div>
			<div
				class="lg:border-l lg:border-l-black lg:border-t-0 border-t border-t-black flex lg:flex-col flex-row stretch"
			>
				<div
					class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
					on:click={() => {
						selected_play_thing = SelectedPlayThing.Select;
					}}
					on:keyup={() => {
						selected_play_thing = SelectedPlayThing.Select;
					}}
					class:shadow-2xl={selected_play_thing === SelectedPlayThing.Select}
					class:opacity-70={selected_play_thing !== SelectedPlayThing.Select}
				>
					<div
						class="rounded-lg bg-emerald-300 w-fit p-1 bg-lime-500 hover:bg-lime-400 transition shadow-lg"
					>
						<svg
							aria-label="Mouse-Click icon"
							class="w-8 h-8 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"
							/>
						</svg>
					</div>
					<h5 class="text-xl w-fit dark:text-black">{$t('index_page.select_answer')}</h5>
					<p class="dark:text-black">{$t('index_page.choose_answer_wisely')}</p>
				</div>
				<div
					class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
					on:click={() => {
						selected_play_thing = SelectedPlayThing.Results;
					}}
					on:keyup={() => {
						selected_play_thing = SelectedPlayThing.Results;
					}}
					class:shadow-2xl={selected_play_thing === SelectedPlayThing.Results}
					class:opacity-70={selected_play_thing !== SelectedPlayThing.Results}
				>
					<div
						class="rounded-lg bg-emerald-300 w-fit p-1 bg-lime-500 hover:bg-lime-400 transition shadow-lg"
					>
						<svg
							aria-label="context-menu icon"
							class="w-8 h-8 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 6h16M4 10h16M4 14h16M4 18h16"
							/>
						</svg>
					</div>
					<h5 class="text-xl dark:text-black">{$t('index_page.view_results')}</h5>
					<p class="dark:text-black">{$t('index_page.check_if_chosen_wisely')}</p>
				</div>
				<div
					class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
					on:click={() => {
						selected_play_thing = SelectedPlayThing.Winners;
					}}
					on:keyup={() => {
						selected_play_thing = SelectedPlayThing.Winners;
					}}
					class:shadow-2xl={selected_play_thing === SelectedPlayThing.Winners}
					class:opacity-70={selected_play_thing !== SelectedPlayThing.Winners}
				>
					<div
						class="rounded-lg bg-emerald-300 w-fit p-1 bg-lime-500 hover:bg-lime-400 transition shadow-lg"
					>
						<svg
							aria-label="sparkling stars-icon"
							class="w-8 h-8 text-black"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
							/>
						</svg>
					</div>
					<h5 class="text-xl dark:text-black">{$t('index_page.list_winners')}</h5>
					<p class="dark:text-black">{$t('index_page.get_ranking_and_winners')}</p>
				</div>
			</div>
		</div>
	</section>

	<section class="mt-24">
		<div class="flex justify-center w-full">
			<h2 class="text-center text-3xl rounded-t-lg bg-opacity-40 bg-white py-2 px-6">
				{$t('index_page.why_classquiz')}
			</h2>
		</div>

		<div
			class="grid grid-rows-2 lg:grid-rows-1 lg:grid-cols-2 bg-opacity-40 bg-white shadow-lg mb-12 lg:mx-12 mx-4 rounded-lg"
		>
			<div>
				<div class="p-12 rounded-lg flex justify-center items-center h-full">
					<p class="dark:text-black">
						{classquiz_reasons[selected_classquiz_reason].content}
					</p>
				</div>
			</div>
			<div
				class="lg:border-l lg:border-l-black lg:border-t-0 border-t border-t-black flex lg:flex-col flex-row stretch overflow-x-auto why-classquiz"
			>
				{#each classquiz_reasons as reason, index}
					<div
						class="m-2 rounded-lg p-2 bg-opacity-40 bg-white transition-all cursor-pointer lg:h-full"
						on:click={() => {
							selected_classquiz_reason = index;
						}}
						on:keyup={() => {
							selected_classquiz_reason = index;
						}}
						class:shadow-2xl={selected_classquiz_reason === index}
						class:opacity-70={selected_classquiz_reason !== index}
					>
						<h5 class="text-xl dark:text-black">{reason.headline}</h5>
					</div>
				{/each}
			</div>
		</div>
	</section>
</div>
{#if newsletterModalOpen}
	<div
		class="fixed bottom-8 right-5 bg-white rounded-lg h-fit w-11/12 ml-5 lg:w-2/12 z-50 p-2 bg-white dark:bg-gray-700"
		transition:fly
	>
		<Newsletter bind:open={newsletterModalOpen} />
	</div>
{/if}
<Footer />

<style>
	.why-classquiz::-webkit-scrollbar {
		height: 0.8rem;
		margin-bottom: 5rem;
	}

	.why-classquiz::-webkit-scrollbar-track {
		box-shadow: inset 0 0 10px 10px transparent;
		border: solid 3px transparent;
	}

	.why-classquiz::-webkit-scrollbar-thumb {
		box-shadow: inset 0 0 10px 10px #374151;
		border: solid 3px transparent;
		border-radius: 15px;
	}

	.why-classquiz::-webkit-scrollbar-thumb:hover {
		box-shadow: inset 0 0 10px 10px #555;
		border: solid 3px transparent;
	}
</style>
