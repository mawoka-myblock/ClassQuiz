<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';

	export let pow_data;
	export let pow_salt;

	const { t } = getLocalization();

	let uppyOpen = false;

	export let edit_id: string;
	export let data: EditorData;

	let custom_bg_color = Boolean(data.background_color);

	$: data.background_color = custom_bg_color ? data.background_color : undefined;
</script>

<div class="w-full h-full pb-20 px-20">
	<div class="rounded-lg bg-white w-full h-full border-gray-500 dark:bg-gray-700">
		<div class="h-fit bg-gray-300 rounded-t-lg dark:bg-gray-500">
			<div class="flex align-middle p-4 gap-3">
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-red-400 transition"
				/>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-yellow-400 transition"
				/>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-green-400 transition"
				/>
			</div>
		</div>
		<div class="dark:bg-gray-700">
			<div class="flex justify-center pt-10 w-full">
				<input
					type="text"
					bind:value={data.title}
					class="p-3 rounded-lg border-gray-500 border text-center w-1/3 text-lg font-semibold dark:bg-gray-500"
				/>
			</div>
			<div class="flex justify-center pt-10 w-full max-h-32">
				<textarea
					type="text"
					bind:value={data.description}
					class="p-3 rounded-lg border-gray-500 border text-center w-1/3 h-20 resize-none dark:bg-gray-500"
				/>
			</div>

			{#if data.cover_image != undefined && data.cover_image !== ''}
				<div class="flex justify-center pt-10 w-full max-h-72 w-full">
					<img
						src={data.cover_image}
						alt="not available"
						class="max-h-72 h-auto w-auto"
						on:contextmenu|preventDefault={() => {
							data.cover_image = '';
						}}
					/>
				</div>
			{:else if pow_data === undefined}
				<a href="/docs/pow" target="_blank" class="cursor-help">
					<Spinner my_20={false} />
				</a>
			{:else}
				{#await import('$lib/editor/uploader.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<svelte:component
						this={c.default}
						bind:modalOpen={uppyOpen}
						bind:edit_id
						bind:data
						bind:pow_data
						bind:pow_salt
					/>
				{/await}
			{/if}
			<div class="pt-10 w-full flex justify-center">
				<button
					type="button"
					on:click={() => {
						data.public = !data.public;
					}}
					class="text-center w-fit"
				>
					{#if data.public}
						<svg
							class="w-8 h-8 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<span>{$t('words.public')}</span>
					{:else}
						<svg
							class="w-8 h-8 inline-block"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
							/>
						</svg>
						<span>{$t('words.private')}</span>
					{/if}
				</button>
			</div>
			<div class="pt-10 w-full flex justify-center">
				<div class="grid grid-cols-3 w-fit h-fit gap-4">
					<div
						class="max-w-full transition-all"
						class:pointer-events-none={custom_bg_color}
						class:opacity-50={custom_bg_color}
					>
						<div class="bg-gray-200 rounded-lg w-full h-full p-1">
							<span
								class="inline-block w-full h-full bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f] dark:bg-[#0f2702] dark:from-[#0f2702] dark:via-[#0f2702] dark:to[#0f2702]"
							/>
						</div>
					</div>
					<div>
						<label
							for="large-toggle"
							class="inline-flex relative items-center cursor-pointer"
						>
							<input
								type="checkbox"
								bind:checked={custom_bg_color}
								id="large-toggle"
								class="sr-only peer"
							/>
							<span
								class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-800 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
							/>
						</label>
					</div>
					<div
						class:pointer-events-none={!custom_bg_color}
						class:opacity-50={!custom_bg_color}
						class="transition-all"
					>
						<input
							type="color"
							class="rounded-lg p-1 min-h-full hover:cursor-pointer"
							bind:value={data.background_color}
						/>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
