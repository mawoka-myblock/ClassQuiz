<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Memory, MemoryCard } from '$lib/quiztivity/types';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let data: Memory | undefined;

	const shuffle = <Type>(a: Array<Type>): Array<Type> => {
		for (let i = a.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[a[i], a[j]] = [a[j], a[i]];
		}
		return a;
	};

	let card_opened = {};

	const get_all_cards_as_single_array = (): MemoryCard[] => {
		console.log('data', data.cards);
		let final_arr: MemoryCard[] = [];
		for (let i = 0; i < data.cards.length; i++) {
			const pair = data.cards[i];
			console.log('pair', pair);
			for (let c = 0; c < pair.length; c++) {
				final_arr.push({ ...pair[c], id: `${i}:${c}` });
				card_opened[`${i}:${c}`] = false;
			}
		}
		console.log(final_arr);
		return final_arr;
	};

	const all_cards_array: MemoryCard[] = get_all_cards_as_single_array();

	const random_card_order = shuffle(all_cards_array);
	console.log(random_card_order);

	const found_cards: string[] = [];
	let opened_active_cards: string[] = [];
	let try_count = 0;
	let game_finished = false;
	const flip_card = (id: string) => {
		if (found_cards.includes(id) || game_finished) {
			return;
		}
		card_opened[id] = true;
		opened_active_cards.push(id);

		if (opened_active_cards.length === 2) {
			const [pair_1_id, card_1_id] = opened_active_cards[0].split(':');
			if (!pair_1_id || !card_1_id) {
				throw "Mustn't happen";
			}
			const [pair_2_id, card_2_id] = opened_active_cards[1].split(':');
			if (!pair_2_id || !card_2_id) {
				throw "Mustn't happen";
			}
			if (pair_2_id === pair_1_id) {
				found_cards.push(opened_active_cards[0]);
				found_cards.push(opened_active_cards[1]);
				opened_active_cards = [];
			}
		}
		if (opened_active_cards.length === 3) {
			card_opened[opened_active_cards[0]] = false;
			card_opened[opened_active_cards[1]] = false;
			opened_active_cards.splice(0, 2);
			try_count += 1;
		}
		game_finished = random_card_order.length === found_cards.length;
	};
</script>

<div>
	<p class="text-center">{$t('quiztivity.play.memory.try_count', { try_count })}</p>
	<div class="grid lg:grid-cols-6 grid-cols-2 gap-2 m-4">
		{#each random_card_order as card}
			<button
				class="aspect-square flex border-[#B07156] border-2 rounded"
				on:click={() => {
					flip_card(card.id);
				}}
			>
				{#if card_opened[card.id]}
					<p class="m-auto transition-all">{card.text}</p>
				{:else}
					<img
						src="/android-chrome-512x512.png"
						alt="ClassQuiz logo"
						class="m-4 opacity-50 hover:opacity-80 transition-all"
					/>
				{/if}
			</button>
		{/each}
	</div>
</div>
