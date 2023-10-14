<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { fly } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';
	import { createEventDispatcher } from 'svelte';
	import { PopoverTypes } from './smalltop';

	const { t } = getLocalization();

	const dispatch = createEventDispatcher();

	export let open = false;
	export let type: PopoverTypes;
	export let data: undefined | { game_pin: number | string; game_id: string } | string =
		undefined;

	$: dispatch('open', open);
</script>

{#if open}
	<div class="fixed w-screen top-10 z-[60] flex justify-center" transition:fly={{ y: -100 }}>
		<div
			class="flex items-center p-4 w-full max-w-xs text-gray-500 bg-white rounded-lg shadow dark:text-gray-400 dark:bg-gray-800"
			role="alert"
		>
			<div class="ml-3 text-sm font-normal">
				{#if type === PopoverTypes.Copy}
					{$t('components.popover.copied_to_clipboard')}
				{:else if type === PopoverTypes.GameInLobby}A game is currently in the lobby. Click <a
						class="underline"
						href="/remote?game_pin={data.game_pin}&game_id={data.game_id}">here</a
					> to join as a remote.
				{:else if type === PopoverTypes.Generic}
					{@html data}
				{:else}
					<p>Error!!!</p>
				{/if}
			</div>
			<button
				type="button"
				class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700"
				data-dismiss-target="#toast-default"
				aria-label="Close"
				on:click={() => {
					open = false;
				}}
			>
				<span class="sr-only">{$t('words.close')}</span>
				<svg
					aria-hidden="true"
					class="w-5 h-5"
					fill="currentColor"
					viewBox="0 0 20 20"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						fill-rule="evenodd"
						d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>
		</div>
	</div>
{/if}
