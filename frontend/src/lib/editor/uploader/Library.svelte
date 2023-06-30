<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PrivateImageData } from '$lib/quiz_types';
	import Spinner from '$lib/Spinner.svelte';
	import type { EditorData } from '$lib/quiz_types';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';

	export let data: EditorData;
	export let selected_question: number;
	export let modalOpen: boolean;

	const { t } = getLocalization();

	const fetch_images = async (): Promise<PrivateImageData> => {
		const response = await fetch('/api/v1/storage/list/last?count=50');
		return await response.json();
	};
	let image_fetch = fetch_images();

	const set_image = (id: string) => {
		if (selected_question === undefined) {
			data.cover_image = id;
		} else if (selected_question === -1) {
			data.background_image = id;
		} else {
			data.questions[selected_question].image = id;
		}
		modalOpen = false;
	};
</script>

{#await image_fetch}
	<Spinner />
{:then images}
	<div class="flex w-screen p-8 h-screen">
		<div
			class="flex flex-col w-1/3 m-auto overflow-scroll h-full rounded p-4 gap-4 bg-white dark:bg-gray-700"
		>
			{#each images as image}
				<div class="rounded border-2 border-[#B07156] p-2 flex-col flex gap-2">
					<div>
						<img
							src="/api/v1/storage/download/{image.id}"
							loading="lazy"
							alt={image.alt_text}
							class="object-contain w-full h-full max-h-full rounded"
						/>
					</div>
					<p class="text-center">{image.filename ?? 'No name available'}</p>
					<BrownButton
						on:click={() => {
							set_image(image.id);
						}}>{$t('words.select')}</BrownButton
					>
				</div>
			{/each}
		</div>
	</div>
{/await}
