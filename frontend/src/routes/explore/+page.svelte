<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { navbarVisible } from '$lib/stores';

	navbarVisible.set(true);
	import SearchCard from '$lib/search-card.svelte';
	import type { PageData } from './$types';

	export let data: PageData;

	const quizzes = data.results;
</script>

<svelte:head>
	<title>ClassQuiz - Explore</title>
</svelte:head>

<div class="grid lg:grid-cols-3 grid-cols-1">
	{#each quizzes.hits as quiz}
		<SearchCard {quiz} />
	{/each}
</div>
