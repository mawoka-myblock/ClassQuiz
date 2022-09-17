<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	import { page } from '$app/stores';
	import { getLocalization } from '$lib/i18n';

	navbarVisible.set(true);
	let status = $page.status;
	const { t } = getLocalization();
</script>

<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<svelte:head>
	<title>{$t('words.error')} - {status}</title>
</svelte:head>
<h1 class="text-6xl text-center">{status}</h1>

{#if status === 404}
	<p class="text-center">
		{$t('error_page.404_text')}
	</p>
{:else}
	<p>
		{$t('error_page.unknown_error_text')}
	</p>
{/if}

<div class="flex justify-center mt-8">
	<img
		class="rounded-lg"
		src="https://http.cat/{status}"
		alt="Cat representing the {status}-http error code"
	/>
</div>
