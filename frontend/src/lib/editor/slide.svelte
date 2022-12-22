<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import TextElement from './slides/types/text.svelte';
	import HeadlineElement from './slides/types/headline.svelte';
	import { draggable } from '@neodrag/svelte';
	import type { Question } from '$lib/quiz_types';
	import { ElementTypes, QuizQuestionType } from '$lib/quiz_types';
	import ElementSelection from './slides/element_selection.svelte';
	import SettingsMenu from './slides/settings_menu.svelte';
	import { onMount } from 'svelte';

	export let data: Question = {
		type: QuizQuestionType.SLIDE,
		time: '120',
		question: '',
		image: undefined,
		answers: []
	};
	let selected_element = undefined;

	let elements_binds: Array<HTMLElement> | undefined = [];
	let main_el: undefined | HTMLElement;
	let settings_menu_open = false;
	const get_location = (id: number): { row: number; col: number } => {
		const numColumns = 12;
		const row = Math.floor(id / numColumns);
		const col = id % numColumns;
		return { row, col };
	};

	const set_correct_position = (
		e: CustomEvent<{ offsetX: number; offsetY: number; domRect: DOMRect }>
	) => {
		const id = parseInt(e.target.getAttribute('el_id'));
		data.answers[id].x = e.detail.offsetX / main_el.offsetWidth;
		data.answers[id].y = e.detail.offsetY / main_el.offsetHeight;
	};

	const set_correct_height = new ResizeObserver((e) => {
		for (const i of e) {
			const id = parseInt(i.target.getAttribute('el_id'));
			data.answers[id].width = i.contentRect.width / main_el.offsetWidth;
			data.answers[id].height = i.contentRect.height / main_el.offsetHeight;
		}
	});
	const add_text_field = () => {
		data.answers = [
			...data.answers,
			{
				type: selected_element,
				data: '',
				x: 0,
				y: 0,
				id: data.answers.length,
				height: 0,
				width: 0
			}
		];
		selected_element = undefined;
	};

	const delete_element = (id: number) => {
		if (!confirm('Do you really want to delete this element?')) {
			return;
		}
		data.answers.splice(id, 1);
		data.answers = data.answers;
		elements_binds.splice(id, 1);
		elements_binds = elements_binds;
	};

	$: {
		if (selected_element) {
			add_text_field();
		}
	}
	const assign_resize_handlers = () => {
		for (let i = 0; i < elements_binds.length; i++) {
			set_correct_height.observe(elements_binds[i]);
		}
	};

	/*	if (data.answers.length !== 0) {
			for (let i = 0; i < data.answers.length; i++) {
				data.answers[i].width = data.answers[i].width * main_el.offsetWidth;
				data.answers[i].height = data.answers[i].height * main_el.offsetHeight;
			}
		}*/

	$: {
		elements_binds;
		assign_resize_handlers();
	}

	const set_correct_size = (e: UIEvent) => {
		console.log(e, 'resized');
	};

	onMount(() => {
		setTimeout(() => {
			for (let i = 0; i < data.answers.length; i++) {
				elements_binds[i].style.height = `${
					data.answers[i].height * main_el.offsetHeight
				}px`;
				elements_binds[i].style.width = `${data.answers[i].width * main_el.offsetWidth}px`;
			}
		}, 100);
	});
</script>

<div class="flex h-full relative w-full pb-12" bind:this={main_el}>
	<div class="absolute top-0 right-0 flex flex-col pr-2 rounded-t-lg">
		<button
			class="ml-auto"
			on:click={() => {
				selected_element = selected_element === null ? undefined : null;
			}}
			type="button"
			class:add-button={selected_element === null}
		>
			Add element
		</button>
		{#if selected_element === null}
			<ElementSelection bind:selected_element />
		{/if}
	</div>

	<div class="absolute top-0 left-0 flex flex-col pl-2 rounded-t-lg">
		<button
			class="mr-auto"
			on:click={() => {
				settings_menu_open = !settings_menu_open;
			}}
			type="button"
		>
			Settings
		</button>
		{#if settings_menu_open}
			<SettingsMenu bind:time={data.time} bind:title={data.question} />
		{/if}
	</div>
	{#if main_el}
		{#each data.answers as el, i}
			<div
				use:draggable={{
					bounds: 'parent',
					handle: '.drag',
					defaultPosition: {
						x: data.answers[i].x * main_el.offsetWidth,
						y: data.answers[i].y * main_el.offsetHeight
					}
				}}
				class="resize h-fit overflow-auto relative min-h-fit"
				on:neodrag:end={set_correct_position}
				el_id={i}
				on:resize={set_correct_size}
				bind:this={elements_binds[el.id]}
			>
				<span
					class="absolute drag dark:text-black hover:cursor-grab opacity-30 hover:opacity-100 transition top-0 left-0"
				>
					<!-- heroicons/arrows-expand -->
					<svg
						class="w-4 h-4"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
						/></svg
					></span
				>
				<!--	<button class='absolute drag dark:text-black opacity-30 hover:opacity-100 transition top-0 right-0' on:click={() => {delete_element(i)}}>
						&lt;!&ndash; heroicons/trash &ndash;&gt;
						<svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'
							 xmlns='http://www.w3.org/2000/svg'>
							<path stroke-linecap='round' stroke-linejoin='round' stroke-width='2'
								  d='M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16'></path>
						</svg>
					</button>-->
				{#if el.type === ElementTypes.Text}
					<TextElement bind:data={el.data} />
				{:else if el.type === ElementTypes.Headline}
					<HeadlineElement bind:data={el.data} />
				{/if}
			</div>
		{/each}
	{/if}
</div>
