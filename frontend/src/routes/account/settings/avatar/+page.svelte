<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { fade, fly } from 'svelte/transition';
	import { bounceOut } from 'svelte/easing';
	import Spinner from '$lib/Spinner.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	const item_count = {
		skin_color: 7,
		top_type: 35,
		hair_color: 10,
		facial_hair_type: 6,
		facial_hair_color: 10,
		mouth_type: 12,
		eyebrow_type: 13,
		accessories_type: 7,
		hat_color: 15,
		clothe_type: 9,
		clothe_color: 15,
		clothe_graphic_type: 11
	};

	const translation_map = {
		skin_color: $t('avatar_settings.skin_color'),
		top_type: $t('avatar_settings.top_type'),
		hair_color: $t('avatar_settings.hair_color'),
		facial_hair_type: $t('avatar_settings.facial_hair_type'),
		facial_hair_color: $t('avatar_settings.facial_hair_color'),
		mouth_type: $t('avatar_settings.mouth_type'),
		eyebrow_type: $t('avatar_settings.eyebrow_type'),
		accessories_type: $t('avatar_settings.accessories_type'),
		hat_color: $t('avatar_settings.hat_color'),
		clothe_type: $t('avatar_settings.clothe_type'),
		clothe_color: $t('avatar_settings.clothe_color'),
		clothe_graphic_type: $t('avatar_settings.clothe_graphic_type')
	};

	let data = {
		skin_color: 0,
		top_type: 0,
		hair_color: 0,
		facial_hair_type: 0,
		facial_hair_color: 0,
		mouth_type: 0,
		eyebrow_type: 0,
		accessories_type: 0,
		hat_color: 0,
		clothe_type: 0,
		clothe_color: 0,
		clothe_graphic_type: 0
	};

	const data_keys = Object.keys(data);
	let index = 0;
	// let index = 10;
	let save_finished: undefined | boolean = undefined;
	let finished = false;

	let image_url;

	$: console.log('index', index);
	const get_image_url = (input_data) => {
		return `/api/v1/avatar/custom?${new URLSearchParams(input_data).toString()}`;
	};
	$: image_url = get_image_url(data);

	const save_avatar = async () => {
		save_finished = false;
		const res = await fetch(`/api/v1/avatar/save?${new URLSearchParams(data).toString()}`, {
			method: 'POST'
		});
		if (res.ok) {
			save_finished = true;
		}
	};
</script>

<div class="h-full">
	<div class="grid grid-cols-6 overflow-hidden h-full">
		<div class="border-r-4 border-black h-full">
			<img src={image_url} />
		</div>
		<div class="col-start-2 col-end-7 overflow-scroll">
			<div class="flex pl-2">
				<div class="mr-auto">
					<BrownButton
						on:click={() => {
							index = index - 1;
						}}
						disabled={index < 1}>{$t('words.back')}</BrownButton
					>
				</div>
				<div class="mx-auto">
					<h2 class="text-2xl">
						{translation_map[data_keys[index]]} ({index + 1}/{data_keys.length})
					</h2>
				</div>
				<div class="ml-auto">
					<BrownButton disabled={index < 11}>{$t('words.finish')}</BrownButton>
				</div>
			</div>
			<div class="grid grid-cols-4">
				{#each Array.from(Array(item_count[data_keys[index]]).keys()) as key}
					<button
						class="hover:opacity-80 transition-all"
						on:click={() => {
							data[data_keys[index]] = key;
							if (index < 11) {
								index++;
							} else {
								save_finished = undefined;
								finished = true;
							}
						}}
					>
						<img
							src={get_image_url({ ...data, [data_keys[index]]: key })}
							in:fade={{ duration: 100 }}
						/>
					</button>
				{/each}
			</div>
		</div>
	</div>
</div>
{#if finished}
	<div
		class="fixed top-0 left-0 w-full h-full z-30 bg-black flex justify-center flex-col bg-opacity-90"
		out:fade={{ duration: 200 }}
		in:fade={{ duration: 300 }}
	>
		<h1 class="m-auto text-4xl" in:fade={{ delay: 3500 }}>{$t('avatar_settings.thats_you')}</h1>
		<img
			class="m-auto w-1/2 h-1/2 z-20"
			src={get_image_url(data)}
			in:fly={{ delay: 500, duration: 4000, y: -500, easing: bounceOut }}
		/>
		<div class="m-auto grid grid-cols-2 gap-4" in:fade={{ delay: 3500 }}>
			<BrownButton
				on:click={() => {
					index = 0;
					finished = false;
				}}>{$t('avatar_settings.start_over')}</BrownButton
			>
			<BrownButton on:click={save_avatar} flex={true} disabled={save_finished === true}>
				{#if save_finished === undefined}{$t('words.save')}
				{:else if save_finished === true}
					<svg
						class="h-6 w-6"
						aria-hidden="true"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
					</svg>
				{:else if save_finished === false}
					<Spinner my_20={false} />
				{/if}
			</BrownButton>
			<BrownButton href="/account/settings">{$t('avatar_settings.go_back')}</BrownButton>
			<BrownButton
				on:click={() => {
					finished = false;
				}}>{$t('words.close')}</BrownButton
			>
		</div>
	</div>
{/if}
