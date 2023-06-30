<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Question } from '$lib/quiz_types';
	import { ElementTypes, QuizQuestionType } from '$lib/quiz_types';
	import ElementSelection from './slides/element_selection.svelte';
	import SettingsMenu from './slides/settings_menu.svelte';
	import { onMount } from 'svelte';
	import Pikaso from 'pikaso';
	import EditMenu from './slides/edit_menu.svelte';
	import type { Konva, ShapeModel } from 'pikaso';
	import { browser } from '$app/environment';

	export let data: Question = {
		type: QuizQuestionType.SLIDE,
		time: '120',
		question: '',
		image: undefined,
		answers: ''
	};
	let selected_element = undefined;
	let canvas_el: HTMLDivElement | undefined;
	let canvas: Pikaso;
	let selected_el: null | ShapeModel<Konva.Shape | Konva.Group, Konva.ShapeConfig> = null;

	let elements_binds: Array<HTMLElement> | undefined = [];
	let main_el: undefined | HTMLElement;
	let settings_menu_open = false;

	const set_correct_height = new ResizeObserver((e) => {
		for (const i of e) {
			const id = parseInt(i.target.getAttribute('el_id'));
			data.answers[id].width = i.contentRect.width / main_el.offsetWidth;
			data.answers[id].height = i.contentRect.height / main_el.offsetHeight;
		}
	});

	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}
	const add_text_field = () => {
		if (selected_element === ElementTypes.Text) {
			canvas.shapes.label.insert({
				container: {
					x: 40,
					y: 40
				},
				text: {
					text: 'Text',
					fontSize: 20
				}
			});
		} else if (selected_element === ElementTypes.Headline) {
			canvas.shapes.label.insert({
				container: {
					x: 40,
					y: 40
				},
				text: {
					text: 'Headline',
					fontSize: 35
				}
			});
		} else if (selected_element === ElementTypes.Circle) {
			canvas.shapes.circle.insert({
				x: 40,
				y: 40,
				radius: 50,
				fill: '#ff000d'
			});
		} else if (selected_element === ElementTypes.Rectangle) {
			canvas.shapes.rect.insert({
				x: 40,
				y: 40,
				width: 50,
				height: 50,
				fill: '#ff000d'
			});
		}
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

	onMount(() => {
		/*		setTimeout(() => {
					for (let i = 0; i < data.answers.length; i++) {
						elements_binds[i].style.height = `${
							data.answers[i].height * main_el.offsetHeight
						}px`;
						elements_binds[i].style.width = `${data.answers[i].width * main_el.offsetWidth}px`;
					}
				}, 200);*/
		canvas = new Pikaso({
			container: canvas_el,
			snapToGrid: {},
			/*			transformer: {
							borderStroke: "#00ff00",
							anchorStroke: "#00ff00"
						},
						cropper: {
							transformer: {
								borderStroke: "#00ff00",
								// anchorFill: "#00ff00",
								anchorStroke: "#00ff00"
							},
							guides: {
								color: "#00ff00"
							}
						},*/
			selection: {
				transformer: {
					borderStroke: darkMode ? '#fff' : '#000000',
					anchorStroke: darkMode ? '#fff' : '#000000'
				}
			}
			/*			selection: {
							interactive: false
						}*/
		});
		if (data.answers) {
			if (typeof data.answers === 'string') {
				canvas.import.json(JSON.parse(data.answers));
			}
		}
		canvas.on('*', () => {
			data.answers = JSON.stringify(canvas.export.toJson());
		});
		canvas.on('selection:change', (data) => {
			/*			data.shapes[0].update({fill: "#ffffff"})
						console.log(data.shapes[0])*/
			// console.log(canvas.board.shapes)
			if (data.shapes.length > 0) {
				selected_el = data.shapes[0];
			} else {
				selected_el = null;
			}
		});
	});
</script>

<div class="flex h-full relative w-full" bind:this={main_el}>
	<div class="absolute top-0 left-0 grid grid-cols-6 w-full">
		<div class="flex flex-col pl-2 rounded-t-lg z-40 pt-2">
			<button
				class="mr-auto"
				on:click={() => {
					settings_menu_open = !settings_menu_open;
				}}
				type="button"
			>
				<svg
					class="w-6 h-6"
					stroke-width="2"
					viewBox="0 0 24 24"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					color="currentColor"
				>
					<path
						d="M12 15a3 3 0 100-6 3 3 0 000 6z"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
					<path
						d="M19.622 10.395l-1.097-2.65L20 6l-2-2-1.735 1.483-2.707-1.113L12.935 2h-1.954l-.632 2.401-2.645 1.115L6 4 4 6l1.453 1.789-1.08 2.657L2 11v2l2.401.655L5.516 16.3 4 18l2 2 1.791-1.46 2.606 1.072L11 22h2l.604-2.387 2.651-1.098C16.697 18.831 18 20 18 20l2-2-1.484-1.75 1.098-2.652 2.386-.62V11l-2.378-.605z"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</button>
			{#if settings_menu_open}
				<SettingsMenu bind:time={data.time} bind:title={data.question} />
			{/if}
		</div>
		<div class="col-start-2 col-end-6 transition bg-transparent pt-2">
			<EditMenu bind:selected_el />
		</div>

		<div class="flex flex-col pr-2 rounded-t-lg z-40 pt-2">
			<button
				class="ml-auto"
				on:click={() => {
					selected_element = selected_element === null ? undefined : null;
				}}
				type="button"
				class:add-button={selected_element === null}
			>
				<svg
					class="w-6 h-6"
					stroke-width="2"
					viewBox="0 0 24 24"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					color="currentColor"
				>
					<path
						d="M9 12h3m3 0h-3m0 0V9m0 3v3M21 3.6v16.8a.6.6 0 01-.6.6H3.6a.6.6 0 01-.6-.6V3.6a.6.6 0 01.6-.6h16.8a.6.6 0 01.6.6z"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</button>
			{#if selected_element === null}
				<ElementSelection bind:selected_element />
			{/if}
		</div>
	</div>
	<div bind:this={canvas_el} class="w-full h-full block" />
</div>
