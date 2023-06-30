<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { ElementTypes } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let selected_element;
	const keybinding_list = {
		t: ElementTypes.Text,
		h: ElementTypes.Headline,
		r: ElementTypes.Rectangle,
		c: ElementTypes.Circle
		// "i": ElementTypes.Image
	};

	const keypress_listener = (key: KeyboardEvent) => {
		if (selected_element !== null) {
			return;
		}
		const sel_type = keybinding_list[key.key];
		if (sel_type) {
			selected_element = sel_type;
		} else if (key.code === 'Escape') {
			selected_element = undefined;
		}
	};

	onMount(() => {
		document.body.addEventListener('keydown', keypress_listener);
	});
	const element_list: Array<{
		name: string;
		description: string;
		type: ElementTypes;
		icon: string | undefined;
		shortcut: string;
	}> = [
		{
			name: $t('editor.slide.headline'),
			description: $t('editor.slide.headline_description'),
			type: ElementTypes.Headline,
			icon: undefined,
			shortcut: 'h'
		},
		{
			name: $t('editor.slide.text'),
			description: $t('editor.slide.text_description'),
			type: ElementTypes.Text,
			icon: undefined,
			shortcut: 't'
		},
		{
			name: $t('editor.slide.rectangle'),
			description: $t('editor.slide.rectangle_description'),
			type: ElementTypes.Rectangle,
			icon: undefined,
			shortcut: 'r'
		},
		{
			name: 'Circle',
			description: 'Just a circle',
			type: ElementTypes.Circle,
			icon: undefined,
			shortcut: 'c'
		}
	];
</script>

<div
	class="bg-white m-auto rounded-lg shadow-lg p-4 flex flex-col dark:bg-gray-600 h-fit"
	transition:fade={{ duration: 100 }}
>
	<ul>
		{#each element_list as el}
			<li
				class="flex flex-row mt-4 w-full bg-gray-200 shadow-xl rounded-lg p-2 hover:bg-gray-300 hover:shadow-2xl hover:cursor-pointer transition dark:bg-gray-800"
				on:click={() => {
					selected_element = el.type;
				}}
			>
				<div class="flex flex-col">
					<h3 class="text-xl">{el.name}</h3>
					<p>{el.description}</p>
				</div>
				<kbd class="my-auto ml-auto">{el.shortcut}</kbd>
			</li>
		{/each}
	</ul>
</div>
