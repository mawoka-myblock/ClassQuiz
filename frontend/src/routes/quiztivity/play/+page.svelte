<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import type { QuizTivityPage } from '$lib/quiztivity/types';
	import { QuizTivityTypes } from '$lib/quiztivity/types';
	import NavigationBar from './navigation_bar.svelte';

	export let data: PageData;
	let quiztivity = data.quiztivity;
	for (let i = 0; i < quiztivity.pages.length; i++) {
		const id = (Math.random() + 1).toString(36).substring(7);
		const type: QuizTivityTypes = quiztivity.pages[i].type as QuizTivityTypes;
		quiztivity.pages[i] = { ...quiztivity.pages[i], id, type };
	}

	let current_slide_index = 0;
	let current_slide: QuizTivityPage = quiztivity.pages[current_slide_index];
	$: current_slide = quiztivity.pages[current_slide_index];
</script>

<div class="w-full h-full flex flex-col overflow-scroll">
	<div class="w-full h-full">
		{#if current_slide.type === QuizTivityTypes.MARKDOWN}
			{#await import('$lib/quiztivity/components/markdown/play.svelte') then c}
				<svelte:component this={c.default} data={current_slide.data} />
			{/await}
		{:else if current_slide.type === QuizTivityTypes.MEMORY}
			{#await import('$lib/quiztivity/components/memory/play.svelte') then c}
				<svelte:component this={c.default} data={current_slide.data} />
			{/await}
		{:else if current_slide.type === QuizTivityTypes.ABCD}
			{#await import('$lib/quiztivity/components/abcd/play.svelte') then c}
				<svelte:component this={c.default} data={current_slide.data} />
			{/await}
		{/if}
	</div>
	<NavigationBar bind:current_slide_index question_count={quiztivity.pages.length} />
</div>
