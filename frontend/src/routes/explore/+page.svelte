<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import { goto } from '$app/navigation';
	import { getLocalization } from '$lib/i18n';
	import SearchCard from '$lib/search-card.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import Search from '@lucide/svelte/icons/search';
	import type { PageData } from './$types';

	navbarVisible.visible = true;

	const { t } = getLocalization();

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	// Seeded from the URL and re-seeded whenever the load reruns, so the box still
	// holds the term after a back/forward navigation. The old search page kept the
	// term in component state and pushed the URL by hand, which meant Back changed the
	// address bar and left the results and the box alone.
	// A writable $derived: typing reassigns it, and a navigation that changes `data.q`
	// resets it to whatever the URL says.
	let term = $derived(data.q);

	// Explicit submit rather than searching as you type: every keystroke would be a
	// Meilisearch request, and the URL is the state here.
	const submit = (event: Event) => {
		event.preventDefault();
		const q = term.trim();
		goto(q === '' ? '/explore' : `/explore?q=${encodeURIComponent(q)}`, {
			keepFocus: true,
			noScroll: true
		});
	};
</script>

<svelte:head>
	<title>frogQuiz - {$t('words.explore')}</title>
</svelte:head>

<!-- fq-section, not fq-stage: fq-stage is min-height:100dvh plus justify-center, which
     is the projector composition. This is a list that can be any length. -->
<div class="fq-section px-4 py-10 sm:px-6">
	<div class="w-full max-w-5xl">
		<h1 class="text-2xl font-semibold tracking-tight">{$t('words.explore')}</h1>

		<form class="mt-4 flex gap-2" onsubmit={submit}>
			<Input
				type="search"
				class="min-w-0 flex-1"
				bind:value={term}
				placeholder={$t('search_page.at_least_3_characters')}
				aria-label={$t('words.search')}
			/>
			<Button type="submit" class="shrink-0">
				<Search />
				<span class="sr-only sm:not-sr-only">{$t('words.search')}</span>
			</Button>
		</form>

		{#if data.failed}
			<p class="text-destructive mt-10 text-center text-sm" role="alert">
				{$t('explore_page.search_failed')}
			</p>
		{:else if data.mode === 'too_short'}
			<p class="text-muted-foreground mt-10 text-center text-sm">
				{$t('search_page.at_least_3_characters')}
			</p>
		{:else if data.hits.length === 0}
			<div class="mt-10 text-center">
				<p class="text-lg font-medium">{$t('search_page.nothing_here')}</p>
				<!-- The old empty state was hardcoded English pointing at /import, which
				     needs an account. Anyone can make a quiz without one. -->
				<p class="text-muted-foreground mt-2 text-sm">
					{$t('explore_page.nothing_here_detail')}
				</p>
				<Button href="/create" class="mt-4">{$t('explore_page.create_one')}</Button>
			</div>
		{:else}
			<div class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each data.hits as quiz (quiz.id)}
					<SearchCard {quiz} />
				{/each}
			</div>
		{/if}
	</div>
</div>
