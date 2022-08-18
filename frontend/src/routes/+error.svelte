<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script context="module">
	throw new Error(
		'@migration task: Replace error load function (https://github.com/sveltejs/kit/discussions/5774#discussioncomment-3293209)'
	);

	// /** @type {import('@sveltejs/kit').Load} */ export function load({ error, status }) {
	// 	return {
	// 		props: {
	// 			status,
	// 			message: error.message
	// 		}
	// 	};
	// }
</script>

<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	navbarVisible.set(true);
	export let status: number;
	export let message: string;
</script>

<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<svelte:head>
	<title>Error - {status}</title>
</svelte:head>
<h1 class="text-6xl text-center">{status}</h1>

{#if status === 404}
	<p class="text-center">
		The page you were looking for is gone or never even existed. Who knows?
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
