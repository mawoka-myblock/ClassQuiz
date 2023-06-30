<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Memory } from '$lib/quiztivity/types';
	import { getLocalization } from '$lib/i18n';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { flip } from 'svelte/animate';

	const { t } = getLocalization();

	export let data: Memory | undefined;
	let new_pair_data = {
		text_1: '',
		text_2: ''
	};

	if (!data) {
		data = {
			cards: []
		};
	}
	const arraymove = (arr: any[], fromI: number, toI: number) => {
		const el = arr[fromI];
		arr.splice(fromI, 1);
		arr.splice(toI, 0, el);
	};
	const move_card_left = (selected_slide: number) => {
		arraymove(data.cards, selected_slide, selected_slide - 1);
		data.cards = data.cards;
	};

	const move_card_right = (selected_slide: number) => {
		arraymove(data.cards, selected_slide, selected_slide + 1);
		data.cards = data.cards;
	};

	const add_card = () => {
		if (!new_pair_data.text_1 || !new_pair_data.text_2) {
			return;
		}
		const id = (Math.random() + 1).toString(36).substring(7);
		data.cards = [
			...data.cards,
			[
				{ id, text: new_pair_data.text_1 },
				{ id, text: new_pair_data.text_2 }
			]
		];
		new_pair_data = {
			text_1: '',
			text_2: ''
		};
	};

	// $: console.log(new_pair_data.text_1.replaceAll("\n", "7"))
</script>

<div class="flex justify-center">
	<div class="grid grid-cols-4 w-11/12 gap-4">
		<div class="border-[#B07156] border-2 rounded">
			<h2 class="text-center">{$t('quiztivity.memory.editor.add_card')}</h2>
			<div class="grid grid-cols-2 py-2">
				<div class="px-2 flex flex-col gap-2">
					<textarea
						type="text"
						class="h-auto resize-none bg-transparent outline-none rounded outline-[#B07156] outline"
						rows="3"
						contenteditable="true"
						bind:value={new_pair_data.text_1}
					/>
					<div class="flex justify-center">
						<span class="h-0.5 bg-black block w-11/12" />
					</div>
					<BrownButton>{$t('quiztivity.memory.editor.upload_image')}</BrownButton>
				</div>
				<div class="px-2 flex flex-col gap-2">
					<textarea
						type="text"
						class="h-auto resize-none bg-transparent outline-none rounded outline-[#B07156] outline"
						rows="3"
						contenteditable="true"
						bind:value={new_pair_data.text_2}
					/>
					<div class="flex justify-center">
						<span class="h-0.5 bg-black block w-11/12" />
					</div>
					<BrownButton>{$t('quiztivity.memory.editor.upload_image')}</BrownButton>
				</div>
			</div>
			<div class="flex justify-center p-2">
				<BrownButton on:click={add_card}
					>{$t('quiztivity.memory.editor.add_pair')}</BrownButton
				>
			</div>
		</div>
		{#each data.cards as card_pair, i (card_pair[0].id)}
			<div
				class="border-[#B07156] border-2 rounded group flex flex-col"
				animate:flip={{ duration: 200 }}
			>
				<div class="grid grid-cols-2 py-2 h-full">
					{#each card_pair as card}
						<div class="px-2 flex h-full">
							<p class="m-auto">{card.text}</p>
						</div>
					{/each}
				</div>
				<div class="grid grid-cols-2 p-2 gap-2">
					<BrownButton
						on:click={() => {
							move_card_left(i);
						}}
						disabled={i === 0}>{$t('quiztivity.editor.move_left')}</BrownButton
					>
					<BrownButton
						on:click={() => {
							move_card_right(i);
						}}
						disabled={i + 1 === data.cards.length}
						>{$t('quiztivity.editor.move_right')}</BrownButton
					>
				</div>
			</div>
		{/each}
	</div>
</div>
