<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Konva, ShapeModel } from 'pikaso';
	import { fade } from 'svelte/transition';

	export let selected_el: null | ShapeModel<Konva.Shape | Konva.Group, Konva.ShapeConfig>;

	let opened_dropdown = null;

	let available_modifiers: Array<string> = [];

	const set_available_modifiers = () => {
		available_modifiers = [];
		if (!selected_el) {
			return;
		}
		switch (selected_el.type) {
			case 'label':
				available_modifiers.push('font_size', 'text_color');
				break;
			case 'circle':
				available_modifiers.push('fill_color');
				break;
			case 'rect':
				available_modifiers.push('fill_color');
				break;
		}
	};

	$: {
		selected_el;
		set_available_modifiers();
	}

	const toggle_switch = (el: string) => {
		if (opened_dropdown) {
			opened_dropdown = null;
		} else {
			opened_dropdown = el;
		}
	};

	const change_color = (e: Event) => {
		if (available_modifiers.includes('text_color')) {
			selected_el.updateText({
				fill: e.target.value
			});
		} else if (available_modifiers.includes('fill_color')) {
			selected_el.update({ fill: e.target.value });
		}
		opened_dropdown = null;
	};

	const change_fontsize = (e: Event) => {
		selected_el.updateText({
			fontSize: e.target.value
		});
	};

	$: if (!selected_el) {
		opened_dropdown = null;
	}
</script>

<div class="flex flex-row justify-evenly z-40">
	<div>
		<button
			type="button"
			class="disabled:opacity-50 transition"
			disabled={!(
				available_modifiers.includes('fill_color') ||
				available_modifiers.includes('text_color')
			)}
			on:click={() => {
				toggle_switch('color');
			}}
		>
			<!-- iconoir/color-picker -->
			<svg
				class="w-6 h-6"
				stroke-width="2"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
				color="currentColor"
			>
				<path
					d="M7 13.161l5.464-5.464a1 1 0 011.415 0l2.12 2.12a1 1 0 010 1.415l-1.928 1.929m-7.071 0l-2.172 2.172a.999.999 0 00-.218.327l-1.028 2.496c-.508 1.233.725 2.466 1.958 1.959l2.497-1.028c.122-.05.233-.125.326-.218l5.708-5.708m-7.071 0h7.071M13.878 3.454l2.121 2.121m4.243 4.243l-2.121-2.121m-2.122-2.122l1.414-1.414a1 1 0 011.415 0l.707.707a1 1 0 010 1.414L18.12 7.697m-2.122-2.122l2.122 2.122"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</button>
		{#if opened_dropdown === 'color'}
			<div
				class="bg-white m-auto rounded-lg shadow-lg p-4 dark:bg-gray-600 h-fit gap-2 w-fit auto-cols-min flex absolute z-40"
				transition:fade={{ duration: 100 }}
			>
				<input type="color" on:change={change_color} />
			</div>
		{/if}
	</div>
	<div>
		<button
			type="button"
			class="disabled:opacity-50 transition"
			on:click={() => {
				toggle_switch('font_size');
			}}
			disabled={!available_modifiers.includes('font_size')}
		>
			<!-- iconoir/font-size -->
			<svg
				class="w-6 h-6"
				stroke-width="2"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
				color="currentColor"
			>
				<path
					d="M18 21V11m0 10l-2-2.5m2 2.5l2-2.5M18 11l-2 2m2-2l2 2M9 5v12m0 0H7m2 0h2M15 7V5H3v2"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</button>
		{#if opened_dropdown === 'font_size'}
			<div
				class="bg-white m-auto rounded-lg shadow-lg p-4 dark:bg-gray-600 h-fit gap-2 w-fit auto-cols-min flex absolute z-40"
				transition:fade={{ duration: 100 }}
			>
				<input
					type="range"
					on:change={change_fontsize}
					value={selected_el?.node?.children?.[1]?.attrs?.fontSize}
					min="10"
					max="250"
				/>
			</div>
		{/if}
	</div>
	<div class="flex flex-row gap-2">
		<button
			type="button"
			class="disabled:opacity-50 transition"
			on:click={() => {
				selected_el.update({ zIndex: selected_el.node.getZIndex() + 1 });
			}}
			disabled={!selected_el}
		>
			<!-- iconoir/priority-up -->
			<svg
				class="w-6 h-6"
				stroke-width="2"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
				color="currentColor"
			>
				<path
					d="M11.576 1.424a.6.6 0 01.848 0l10.152 10.152a.6.6 0 010 .848L12.424 22.576a.6.6 0 01-.848 0L1.424 12.424a.6.6 0 010-.848L11.576 1.424zM12 7l4 4m-4-4l-4 4.167M12 7v9"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</button>
		<button
			type="button"
			class="disabled:opacity-50 transition"
			on:click={() => {
				selected_el.update({ zIndex: selected_el.node.getZIndex() - 1 });
			}}
			disabled={!selected_el}
		>
			<!-- iconoir/priority-down -->
			<svg
				class="w-6 h-6"
				stroke-width="2"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
				color="currentColor"
			>
				<path
					d="M11.576 1.424a.6.6 0 01.848 0l10.152 10.152a.6.6 0 010 .848L12.424 22.576a.6.6 0 01-.848 0L1.424 12.424a.6.6 0 010-.848L11.576 1.424zM12 16l4-4m-4 4l-4-4.167M12 16V7"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</button>
	</div>
</div>
