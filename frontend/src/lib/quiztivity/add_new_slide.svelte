<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { QuizTivityTypes } from './types';
	import { getLocalization } from '$lib/i18n';
	import { fade } from 'svelte/transition';

	const { t } = getLocalization();
	export let type: QuizTivityTypes | undefined;

	const PageTypes = [
		/*		{
			name: 'Pdf',
			description: 'Upload a PDF!',
			type: QuizTivityTypes.PDF,
			svg: undefined
		},*/
		{
			name: 'Memory',
			description: 'Matching Pairs game',
			type: QuizTivityTypes.MEMORY,
			svg: undefined
		},
		{
			name: 'Markdown',
			description: 'Add content in Markdown format!',
			type: QuizTivityTypes.MARKDOWN,
			svg: undefined
		},
		{
			name: 'Multiple Choice',
			description: 'Multiple Choice Quiz',
			type: QuizTivityTypes.ABCD,
			svg: undefined
		}
	];
</script>

<div
	class="fixed top-0 left-0 z-50 bg-black bg-opacity-50 flex w-screen h-screen"
	transition:fade={{ duration: 100 }}
>
	<div class="m-auto w-5/6 h-5/6">
		<div class="rounded bg-white p-6 dark:bg-gray-600">
			<h1 class="text-center text-3xl mb-6">{$t('quiztivity.editor.select_page_type')}</h1>
			<div class="grid grid-cols-4 gap-4 overflow-y-scroll">
				{#each PageTypes as pt}
					<div class="rounded p-6 border-[#B07156] border">
						<button
							class="text-xl text-black dark:text-white"
							on:click={() => {
								type = pt.type;
							}}>{pt.name}</button
						>
						<p class="text-sm">{pt.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>
