<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { PageData } from './$types';
	import PlayerOverview from './player_overview.svelte';
	import QuestionOverview from './question_overview.svelte';

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
				>Overview
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
				Players
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
				>Questions
			</button>
		</div>
	</div>
	{#if selected_tab === SelectedTab.Overview}{:else if selected_tab === SelectedTab.Questions}
		<div>
			<QuestionOverview quiz={data.results.quiz} answers={data.results.answers} />
		</div>
	{:else if selected_tab === SelectedTab.Players}
		<div>
			<PlayerOverview
				custom_field={data.results.custom_field_data}
				scores={data.results.player_scores}
			/>
		</div>
	{/if}
</div>
