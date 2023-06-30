<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Data } from './types';
	import { getLocalization } from '$lib/i18n';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import AddNewSlide from './add_new_slide.svelte';
	import { QuizTivityTypes } from './types';
	import PdfEdit from './components/pdf/edit.svelte';
	import MemoryEdit from './components/memory/edit.svelte';
	import MarkdownEdit from './components/markdown/edit.svelte';
	import AbcdEdit from './components/abcd/edit.svelte';
	import { flip } from 'svelte/animate';
	import { createEventDispatcher } from 'svelte';
	import SharesPopover from '$lib/quiztivity/shares_popover.svelte';

	const { t } = getLocalization();
	const dispatch = createEventDispatcher();

	export let data: Data;
	export let saving: boolean;

	let selected_slide = null;
	let opened_slide = null;
	let selected_type = undefined;
	let shares_menu_open = false;

	for (let i = 0; i < data.pages.length; i++) {
		const id = (Math.random() + 1).toString(36).substring(7);
		const type: QuizTivityTypes = data.pages[i].type as QuizTivityTypes;
		data.pages[i] = { ...data.pages[i], id, type };
	}
	const handle_slide_add = (type: QuizTivityTypes | undefined | null) => {
		if (!type) {
			return;
		}
		const id = (Math.random() + 1).toString(36).substring(7);
		data.pages.push({ title: undefined, data: undefined, type, id });
		opened_slide = data.pages.length - 1;
	};
	$: handle_slide_add(selected_type);

	const delete_slide = () => {
		console.log(selected_slide);
		data.pages.splice(selected_slide, 1);
		data.pages = data.pages;
		selected_slide = null;
	};

	const arraymove = (arr: any[], fromI: number, toI: number) => {
		const el = arr[fromI];
		arr.splice(fromI, 1);
		arr.splice(toI, 0, el);
	};
	const move_slide_left = () => {
		arraymove(data.pages, selected_slide, selected_slide - 1);
		selected_slide -= 1;
		data.pages = data.pages;
	};

	const move_slide_right = () => {
		arraymove(data.pages, selected_slide, selected_slide + 1);
		selected_slide += 1;
		data.pages = data.pages;
	};
</script>

{#if opened_slide === null}
	<div>
		<div class="grid grid-cols-3">
			{#if data.id}
				<div class="mr-auto w-fit pl-2">
					<BrownButton
						on:click={() => {
							shares_menu_open = true;
						}}>{$t('quiztivity.editor.open_shares_menu')}</BrownButton
					>
				</div>
			{:else}
				<span />
			{/if}
			<input
				class="bg-transparent outline-none text-center mx-auto"
				placeholder={$t('quiztivity.editor.title_placeholder')}
				bind:value={data.title}
			/>
			<div class="self-end pr-2 w-full">
				<div class="ml-auto w-fit">
					<BrownButton
						on:click={() => {
							dispatch('save');
						}}
						disabled={!data.title}>{$t('words.save')}</BrownButton
					>
				</div>
			</div>
		</div>
		<div class="flex flex-row gap-2 w-full p-2">
			<BrownButton
				on:click={() => {
					selected_type = null;
				}}>{$t('quiztivity.editor.add_new')}</BrownButton
			>
			<BrownButton on:click={delete_slide} disabled={selected_slide === null}
				>{$t('quiztivity.editor.delete')}</BrownButton
			>
			<BrownButton
				on:click={move_slide_left}
				disabled={selected_slide === null || selected_slide === 0}
				>{$t('quiztivity.editor.move_left')}</BrownButton
			>
			<BrownButton
				on:click={move_slide_right}
				disabled={selected_slide === null || selected_slide === data.pages.length - 1}
				>{$t('quiztivity.editor.move_right')}</BrownButton
			>
		</div>
		<div class="flex justify-center mt-6">
			<div class="grid grid-cols-6 gap-6 w-11/12">
				{#each data.pages as page, i (page.id)}
					<div
						class="border-[#B07156] border-2 rounded aspect-square flex flex-col group"
						animate:flip={{ duration: 200 }}
					>
						<p class="m-auto">{page.type}</p>
						<div
							class="grid grid-cols-2 gap-2 p-2 group-hover:opacity-100 transition-all"
							class:opacity-0={selected_slide !== i}
						>
							<BrownButton
								on:click={() => {
									selected_slide = selected_slide === i ? null : i;
								}}
							>
								{#if selected_slide === i}{$t('words.selected')}{:else}{$t(
										'words.select'
									)}{/if}
							</BrownButton>
							<BrownButton
								on:click={() => {
									opened_slide = i;
								}}>{$t('words.edit')}</BrownButton
							>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
{:else}
	{@const sel_t = data.pages[opened_slide].type}
	<div class="h-full">
		<div class="mb-2">
			<BrownButton
				on:click={() => {
					opened_slide = null;
				}}>{$t('words.back')}</BrownButton
			>
		</div>
		{#if sel_t === QuizTivityTypes.PDF}
			<PdfEdit />
		{:else if sel_t === QuizTivityTypes.MEMORY}
			<MemoryEdit bind:data={data.pages[opened_slide].data} />
		{:else if sel_t === QuizTivityTypes.MARKDOWN}
			<MarkdownEdit bind:data={data.pages[opened_slide].data} />
		{:else if sel_t === QuizTivityTypes.ABCD}
			<AbcdEdit bind:data={data.pages[opened_slide].data} />
		{:else}
			<h1 class="text-8xl">ERROR!</h1>
		{/if}
	</div>
{/if}

{#if selected_type === null}
	<AddNewSlide bind:type={selected_type} />
{/if}
{#if shares_menu_open}
	<SharesPopover id={data.id} bind:open={shares_menu_open} />
{/if}
