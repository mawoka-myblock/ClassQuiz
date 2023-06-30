<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';

	export let data: EditorData;
	export let selected_question: number;
	export let modalOpen: boolean;

	let page = 1;
	let search_term = '';
	let loading = false;

	const { t } = getLocalization();

	const set_image = async (id: string) => {
		loading = true;
		const res = await fetch(`/api/v1/pixabay/save?id=${id}`, {
			method: 'POST'
		});
		const json = await res.json();
		const storage_id = json.id;
		if (selected_question === undefined) {
			data.cover_image = storage_id;
		} else if (selected_question === -1) {
			data.background_image = storage_id;
		} else {
			data.questions[selected_question].image = storage_id;
		}
		modalOpen = false;
	};

	const fetch_data = async () => {
		const res = await fetch(`/api/v1/pixabay/images?page=${page}&query=${search_term}`);
		return await res.json();
	};

	let fetched_data = fetch_data();
</script>

{#await fetched_data}
	<Spinner />
{:then data}
	{#if loading}
		<Spinner />
	{:else}
		<div class="flex w-screen p-8 h-full mt-8 mb-1">
			<div
				class="flex flex-col w-1/3 m-auto overflow-scroll h-full rounded p-4 gap-2 bg-white dark:bg-gray-700"
			>
				<h1 class="text-2xl text-center">{$t('uploader.images_by_pixabay')}</h1>
				<div class="flex">
					<a href="https://pixabay.com" target="_blank" class="underline mx-auto"
						>{$t('uploader.visit_pixabay')}</a
					>
				</div>

				<form
					class="w-full flex gap-2"
					on:submit|preventDefault={() => (fetched_data = fetch_data())}
				>
					<input
						class="w-full outline-none p-1 rounded dark:bg-gray-500 bg-gray-300"
						bind:value={search_term}
					/>
					<div class="w-fit">
						<BrownButton type="submit">{$t('words.search')}</BrownButton>
					</div>
				</form>
				<span class="italic text-center text-sm">{$t('uploader.search_english_only')}</span>

				{#each data.hits as image}
					<div class="rounded border-2 border-[#B07156] p-2 flex-col flex gap-2">
						<div>
							<img
								src={image.webformatURL}
								loading="lazy"
								alt="unavailable"
								class="object-contain w-full h-full rounded max-h-[80vh]"
							/>
						</div>
						<BrownButton
							on:click={() => {
								set_image(image.id);
							}}>{$t('words.select')}</BrownButton
						>
					</div>
				{/each}
				<div class="flex gap-2">
					<BrownButton
						disabled={page < 2}
						on:click={() => {
							page -= 1;
							fetched_data = fetch_data();
						}}
						>{$t('uploader.previous_page')}
					</BrownButton>
					<BrownButton
						on:click={() => {
							page += 1;
							fetched_data = fetch_data();
						}}>{$t('uploader.next_page')}</BrownButton
					>
				</div>
			</div>
		</div>
	{/if}
{/await}
