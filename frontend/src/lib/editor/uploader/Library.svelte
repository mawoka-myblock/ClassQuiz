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

	const fetch_files = async (): Promise<PrivateImageData> => {
		const response = await fetch('/api/v1/storage/list/last?count=50');
		return await response.json();
	};
	let files_fetch = fetch_files();

	const set_file = (file: PrivateImageData) => {
		if (selected_question === undefined) {
			data.cover_image = file.id;
		} else if (selected_question === -1) {
			data.background_image = file.id;
		} else {
			if (file.mime_type === 'music/mp3') {
				data.questions[selected_question].music = file.id;
			} else {
				data.questions[selected_question].image = file.id;
			}
		}
		modalOpen = false;
	};
</script>

{#await files_fetch}
	<Spinner />
{:then files}
	<div class="flex w-screen p-8 h-screen">
		<div
			class="flex flex-col w-1/3 m-auto overflow-scroll h-full rounded p-4 gap-4 bg-white dark:bg-gray-700"
		>
			{#each files as file}
				{#if file.mime_type === 'music/mp3'}
					<div class="rounded border-2 border-[#B07156] p-2 flex-col flex gap-2">
						<div>
							<svg
								height="15vh"
								width="100%"
								version="1.1"
								id="Layer_1"
								xmlns="http://www.w3.org/2000/svg"
								xmlns:xlink="http://www.w3.org/1999/xlink"
								viewBox="0 0 496.158 496.158"
								xml:space="preserve"
								class="object-contain w-full h-full max-h-[15vh] rounded"
							>
								<path
									style="fill:#337180;"
									d="M496.158,248.085c0-137.022-111.068-248.082-248.074-248.082C111.07,0.003,0,111.063,0,248.085
					c0,137.001,111.07,248.07,248.084,248.07C385.09,496.155,496.158,385.086,496.158,248.085z"
								/>
								<g>
									<path
										style="fill:#DFF2F4;"
										d="M73.412,251.075c0,3.313-2.686,6-6,6H56.746c-3.314,0-6-2.687-6-6v-6.5c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V251.075z"
									/>
									<path
										style="fill:#DFF2F4;"
										d="M104.412,266.825c0,3.313-2.686,6-6,6H87.746c-3.314,0-6-2.687-6-6v-37.5c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V266.825z"
									/>
								</g>
								<g>
									<path
										style="fill:#B5E3EA;"
										d="M135.412,274.579c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-53c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V274.579z"
									/>
									<path
										style="fill:#B5E3EA;"
										d="M166.412,290.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-84c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V290.079z"
									/>
								</g>
								<g>
									<path
										style="fill:#A3D5E0;"
										d="M197.412,321.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-146c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V321.079z"
									/>
									<path
										style="fill:#A3D5E0;"
										d="M228.412,336.579c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-177c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V336.579z"
									/>
								</g>
								<path
									style="fill:#8EC5CE;"
									d="M259.412,383.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-270c0-3.313,2.686-6,6-6h10.666
					c3.314,0,6,2.687,6,6V383.079z"
								/>
								<g>
									<path
										style="fill:#A3D5E0;"
										d="M290.412,321.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-146c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V321.079z"
									/>
									<path
										style="fill:#A3D5E0;"
										d="M321.412,290.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-84c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V290.079z"
									/>
								</g>
								<g>
									<path
										style="fill:#B5E3EA;"
										d="M352.412,305.579c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-115c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V305.579z"
									/>
									<path
										style="fill:#B5E3EA;"
										d="M383.412,274.575c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-53c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V274.575z"
									/>
								</g>
								<g>
									<path
										style="fill:#DFF2F4;"
										d="M445.412,251.261c0,3.314-2.686,6-6,6h-10.666c-3.314,0-6-2.686-6-6v-6.5c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V251.261z"
									/>
									<path
										style="fill:#DFF2F4;"
										d="M414.412,259.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-22c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V259.079z"
									/>
								</g>
							</svg>
						</div>
						<p class="text-center">{file.filename ?? 'No name available'}</p>
						<BrownButton
							on:click={() => {
								set_file(file);
							}}>{$t('words.select')}</BrownButton
						>
					</div>
				{:else}
					<div class="rounded border-2 border-[#B07156] p-2 flex-col flex gap-2">
						<div>
							<img
								src="/api/v1/storage/download/{file.id}"
								loading="lazy"
								alt={file.alt_text}
								class="object-contain w-full h-full max-h-full rounded"
							/>
						</div>
						<p class="text-center">{file.filename ?? 'No name available'}</p>
						<BrownButton
							on:click={() => {
								set_file(file);
							}}>{$t('words.select')}</BrownButton
						>
					</div>
				{/if}
			{/each}
		</div>
	</div>
{/await}
