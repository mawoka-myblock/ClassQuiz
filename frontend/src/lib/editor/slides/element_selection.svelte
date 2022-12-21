<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { ElementTypes } from '$lib/editor/types';
	import { elementSelection } from '$lib/stores';
	import { onMount } from 'svelte';

	const keybinding_list = {
		t: ElementTypes.Text,
		h: ElementTypes.Headline
		// "i": ElementTypes.Image
	};

	const keypress_listener = (key: KeyboardEvent) => {
		const sel_type = keybinding_list[key.key];
		if (sel_type) {
			elementSelection.set({ data: sel_type });
		} else if (key.code === 'Escape') {
			elementSelection.set({ data: undefined });
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
		}
	];
</script>

<div
	class="fixed top-0 left-0 flex justify-center w-screen h-screen bg-black bg-opacity-60 z-50 text-black"
>
	<div class="w-5/6 h-5/6 bg-white m-auto rounded-lg shadow-lg p-4 flex flex-col">
		<div class="flex justify-center">
			<h1 class="text-2xl">Select the element you want to add</h1>
		</div>
		<ul>
			{#each element_list as el}
				<li
					class="flex flex-row mt-4 w-full bg-gray-200 shadow-xl rounded-lg p-2 hover:bg-gray-300 hover:shadow-2xl hover:cursor-pointer transition"
					on:click={() => {
						elementSelection.set({ data: el.type });
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
</div>
