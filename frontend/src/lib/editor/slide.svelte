<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import TextElement from './slides/types/text.svelte';
	import HeadlineElement from './slides/types/text.svelte';
	import { ElementTypes } from './types';
	import { elementSelection } from '$lib/stores';

	export let data;
	let selected_el_id = undefined;
	elementSelection.set({ data: undefined });

	const ghost_elements = new Array(72).fill({});
	let elements: Array<{
		height: number;
		width: number;
		col: number;
		row: number;
		type: ElementTypes;
		data;
	}> = [];
	let elements_binds = [];
	const get_location = (id: number): { row: number; col: number } => {
		const numColumns = 12;
		const row = Math.floor(id / numColumns);
		const col = id % numColumns;
		return { row, col };
	};

	const add_text_field = (id: number) => {};

	const change_size = (position: string, id: number, increase: boolean) => {
		if (position === 't') {
			elements[id].row += increase ? -1 : 1;
			elements[id].height += increase ? 1 : -1;
		} else if (position === 'b') {
			elements[id].height += increase ? 1 : -1;
		} else if (position === 'l') {
			elements[id].width += increase ? 1 : -1;
			elements[id].col += increase ? -1 : 1;
		} else if (position === 'r') {
			elements[id].width += increase ? 1 : -1;
		}
		if (elements[id].width < 1 || elements[id].height < 1) {
			elements.splice(id, 1);
		}
		if (elements[id].row < 0) {
			elements[id].row = 0;
		}
		if (elements[id].col < 0) {
			elements[id].col = 0;
		}
		console.log(elements[id]);
	};
	let occupied_fields = [];

	elementSelection.subscribe((data) => {
		if (data.data && selected_el_id) {
			console.log('data!', data.data);
			const { row, col } = get_location(selected_el_id);
			elements = [...elements, { height: 1, width: 1, col, row, type: data.data, data: '' }];
			elementSelection.set({ data: undefined });
			occupied_fields.push(selected_el_id);
			selected_el_id = undefined;
		}
	});
</script>

<div class="flex h-full">
	<div
		class="grid grid-cols-12 grid-rows-6 w-full h-full pb-12 absolute overflow-hidden relative max-h-full"
	>
		{#each elements as el, i}
			<div
				class="z-20 overflow-auto relative group"
				element_id={i}
				style="grid-column-start: {el.col + 1}; grid-row-start: {el.row +
					1};grid-column-end: {el.col + 1 + el.width}; grid-row-end: {el.row +
					1 +
					el.height}"
				bind:this={elements_binds[i]}
			>
				<div
					class="absolute top-0 left-0 mx-auto justify-center w-full h-0 hidden group-hover:flex"
				>
					<div>
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('t', i, true);
							}}
							disabled={el.row === 0}
							>+
						</button>
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('t', i, false);
							}}>-</button
						>
					</div>
				</div>
				<div
					class="absolute bottom-6 left-0 mx-auto justify-center w-full h-0 hidden group-hover:flex"
				>
					<div>
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('b', i, true);
							}}
							disabled={el.row + el.height === 6}
							>+
						</button>
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('b', i, false);
							}}>-</button
						>
					</div>
				</div>
				<div
					class="absolute top-0 left-3 mx-auto justify-center h-full w-0 hidden group-hover:flex"
				>
					<div class="my-auto">
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('l', i, true);
							}}
							disabled={el.col === 0}
							>+
						</button>
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('l', i, false);
							}}>-</button
						>
					</div>
				</div>
				<div
					class="absolute top-0 right-3 mx-auto justify-center h-full w-0 hidden group-hover:flex"
				>
					<div class="my-auto">
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('r', i, true);
							}}
							disabled={el.col + el.width === 12}
							>+
						</button>
						<button
							class="text-black z-30"
							on:click={() => {
								change_size('r', i, false);
							}}>-</button
						>
					</div>
				</div>
				{#if el.type === ElementTypes.Text}
					<p>Text</p>
					<TextElement />
				{:else if el.type === ElementTypes.Headline}
					<p>Headline</p>
					<HeadlineElement bind:data={el.data} />
				{/if}
			</div>
		{/each}
	</div>
	<div class="grid grid-cols-12 grid-rows-6 w-full h-full pb-12 absolute overflow-hidden">
		{#each ghost_elements as el, i}
			<div class="w-full border border-gray-600 group">
				<button
					class="h-full flex justify-center w-full dark:text-black invisible group-hover:visible"
					on:click={() => {
						selected_el_id = i;
						elementSelection.set({ data: null });
					}}
				>
					{i}
					<svg
						class="h-12 m-auto"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
				</button>
			</div>
		{/each}
	</div>
</div>
