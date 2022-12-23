<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { ElementTypes } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';

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
			name: 'Headline',
			description: 'A bold text for headlines',
			type: ElementTypes.Headline,
			icon: undefined,
			shortcut: 'h'
		},
		{
			name: 'Text',
			description: 'Smaller longer text',
			type: ElementTypes.Text,
			icon: undefined,
			shortcut: 't'
		},
		{
			name: 'Rectangle',
			description: 'Just a rectangle',
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
