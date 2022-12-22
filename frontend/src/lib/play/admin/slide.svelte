<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import TextElement from '$lib/editor/slides/types/text.svelte';
	import HeadlineElement from '$lib/editor/slides/types/headline.svelte';
	import { ElementTypes } from '$lib/quiz_types.js';
	import { draggable } from '@neodrag/svelte';

	export let question: Question;

	let main_el: HTMLElement | undefined;
</script>

<div class="w-full min-h-[calc(100vh-8rem)]" bind:this={main_el}>
	{#if main_el}
		{#each question.answers as el, i}
			<div
				use:draggable={{
					bounds: 'parent',
					handle: '.drag',
					disabled: true,
					defaultPosition: {
						x: el.x * main_el.offsetWidth,
						y: el.y * main_el.offsetHeight
					}
				}}
				style="height: {el.height * main_el.offsetHeight}px; width: {el.width *
					main_el.offsetWidth}px"
			>
				{#if el.type === ElementTypes.Text}
					<TextElement bind:data={el.data} editor={false} />
				{:else if el.type === ElementTypes.Headline}
					<HeadlineElement bind:data={el.data} editor={false} />
				{/if}
			</div>
		{/each}
	{/if}
</div>
