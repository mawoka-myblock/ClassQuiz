<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import PlayerOverview from './player_overview.svelte';
	import QuestionOverview from './question_overview.svelte';
	import GeneralOverview from './general_overview.svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let data: PageData;

	// eslint-disable-next-line no-unused-vars
	enum SelectedTab {
		// eslint-disable-next-line no-unused-vars
		Overview,
		// eslint-disable-next-line no-unused-vars
		Players,
		// eslint-disable-next-line no-unused-vars
		Questions
	}

	let selected_tab: SelectedTab = SelectedTab.Overview;
</script>

<div class="w-full">
	<div class="flex flex-row w-full justify-around border-b-2 border-gray-500 mb-4">
		<div
			class="w-full py-2 flex transition-all hover:opacity-100"
			class:text-lg={selected_tab === SelectedTab.Overview}
			class:opacity-60={selected_tab !== SelectedTab.Overview}
		>
			<button
				on:click={() => {
					selected_tab = SelectedTab.Overview;
				}}
				class="m-auto w-full h-full"
				>{$t('words.overview')}
			</button>
		</div>
		<div
			class="w-full py-2 flex border-x-2 border-gray-500 transition-all hover:opacity-100"
			class:text-lg={selected_tab === SelectedTab.Players}
			class:opacity-60={selected_tab !== SelectedTab.Players}
		>
			<button
				on:click={() => {
					selected_tab = SelectedTab.Players;
				}}
				class="m-auto w-full h-full"
			>
				{$t('words.player', { count: 2 })}
			</button>
		</div>
		<div
			class="w-full py-2 flex transition-all hover:opacity-100"
			class:text-lg={selected_tab === SelectedTab.Questions}
			class:opacity-60={selected_tab !== SelectedTab.Questions}
		>
			<button
				on:click={() => {
					selected_tab = SelectedTab.Questions;
				}}
				class="m-auto w-full h-full"
				>{$t('words.question', { count: 2 })}
			</button>
		</div>
	</div>
	{#if selected_tab === SelectedTab.Overview}
		<div in:fade={{ duration: 150 }}>
			<GeneralOverview
				questions={data.results.questions}
				answers={data.results.answers}
				scores={data.results.player_scores}
				title={data.results.title}
				timestamp={data.results.timestamp}
			/>
		</div>
	{:else if selected_tab === SelectedTab.Questions}
		<div in:fade={{ duration: 150 }}>
			<QuestionOverview questions={data.results.questions} answers={data.results.answers} />
		</div>
	{:else if selected_tab === SelectedTab.Players}
		<div in:fade={{ duration: 150 }}>
			<PlayerOverview
				custom_field={data.results.custom_field_data}
				scores={data.results.player_scores}
			/>
		</div>
	{/if}
</div>
