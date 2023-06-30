<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	export let data;
	import { fly } from 'svelte/transition';

	const { t } = getLocalization();
</script>

<div class="w-full px-6 lg:px-20 h-[80vh] absolute" in:fly={{ x: 100 }} out:fly={{ x: -100 }}>
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
				<p
					class="p-3 rounded-lg border-gray-500 border text-center w-11/12 lg:w-1/3 text-lg font-semibold dark:bg-gray-500"
				>
					{@html data.title}
				</p>
			</div>
			<div class="flex justify-center pt-10 w-full max-h-32">
				<p
					class="p-3 rounded-lg border-gray-500 border text-center w-11/12 lg:w-1/3 h-20 resize-none dark:bg-gray-500"
				>
					{@html data.description}
				</p>
			</div>

			{#if data.cover_image != undefined && data.cover_image !== ''}
				<div class="flex justify-center pt-10 w-full max-h-72 w-full">
					<img
						src="/api/v1/storage/download/{data.cover_image}"
						alt="not available"
						class="max-h-72 h-auto w-auto"
						on:contextmenu|preventDefault={() => {
							data.cover_image = '';
						}}
					/>
				</div>
			{/if}
			<div class="pt-10 w-full flex justify-center">
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
			</div>
		</div>
	</div>
</div>
