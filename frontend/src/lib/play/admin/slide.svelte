<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { onMount } from 'svelte';
	import Pikaso from 'pikaso';

	export let question: Question;

	let canvas_el: HTMLDivElement | undefined;
	let canvas: Pikaso;
	let img_src = '';

	onMount(() => {
		canvas = new Pikaso({
			container: canvas_el,
			snapToGrid: {},
			selection: {
				interactive: false
			}
		});
		if (typeof question.answers === 'string') {
			const data = JSON.parse(question.answers);
			canvas.import.json(data);
			img_src = canvas.export.toImage();
		}
	});
</script>

<div class="w-full h-full">
	<div class="hidden">
		<div bind:this={canvas_el} class="w-full h-full block" />
	</div>
	<div class="w-full h-full flex justify-center">
		<img src={img_src} />
	</div>
</div>
