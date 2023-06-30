<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	import { page } from '$app/stores';
	navbarVisible.set(true);
	let status = $page.status;
</script>

<svelte:head>
	<title>Error - {status}</title>
</svelte:head>
<h1 class="text-6xl text-center">{status}</h1>

{#if status === 404}
	<p class="text-center">
		The quiz you were looking for is gone or never even existed. Who knows?
	</p>
{:else}
	<p>
		That shouldn't happen. It's probably my fault, not yours, but maybe you have a magical power
		to break stuff...
	</p>
{/if}

<div class="flex justify-center mt-8">
	<img
		class="rounded-lg"
		src="https://http.cat/{status}"
		alt="Cat representing the {status}-http error code"
	/>
</div>
