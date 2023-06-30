<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { createTippy } from 'svelte-tippy';

	export let imported: boolean | undefined;
	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});
</script>

{#if imported === true}
	<svg
		class="w-6 h-6 inline-block h-8 w-8 align-middle"
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
		use:tippy={{ content: 'This quiz is imported from KAHOOT!' }}
		xmlns="http://www.w3.org/2000/svg"
	>
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
		/>
	</svg>
{:else if imported === false}
	<svg
		class="w-6 h-6 inline-block h-8 w-8 align-middle"
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
		use:tippy={{ content: 'This quiz was made by the creator themself!' }}
		xmlns="http://www.w3.org/2000/svg"
	>
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
		/>
	</svg>
{:else}
	<svg
		class="w-6 h-6 inline-block h-8 w-8 align-middle"
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
		use:tippy={{ content: 'This quiz could be imported, it could be OC.' }}
		xmlns="http://www.w3.org/2000/svg"
	>
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
		/>
	</svg>
{/if}
