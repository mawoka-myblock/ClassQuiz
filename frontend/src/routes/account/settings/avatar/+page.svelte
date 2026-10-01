<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
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

	let data = $state({
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
	});

	const data_keys = Object.keys(data);
	let index = $state(0);
	// let index = 10;
	let save_finished: undefined | boolean = $state(undefined);
	let finished = $state(false);
	const get_image_url = (input_data) => {
		return `/api/v1/avatar/custom?${new URLSearchParams(input_data).toString()}`;
	};

	let image_url = $derived(get_image_url(data));

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

<!-- Was a grid-cols-6 with the preview crushed into a one-sixth column behind a
     border-r-4 border-black, the Back/Finish buttons jammed into the heading row, and a
     fixed grid-cols-4 of choices at every width. Preview above the choices on a phone,
     beside them once there is room; the step header is its own row. -->
<div class="mx-auto w-full max-w-4xl px-4 py-6">
	<div class="mb-4 flex items-center justify-between gap-3">
		<Button
			variant="outline"
			size="sm"
			onclick={() => {
				index = index - 1;
			}}
			disabled={index < 1}>{$t('words.back')}</Button
		>
		<h1 class="min-w-0 truncate text-center text-lg font-semibold tracking-tight">
			{translation_map[data_keys[index]]}
			<span class="text-muted-foreground font-normal tabular-nums"
				>({index + 1}/{data_keys.length})</span
			>
		</h1>
		<Button
			size="sm"
			disabled={index < 11}
			onclick={() => {
				save_finished = undefined;
				finished = true;
			}}>{$t('words.finish')}</Button
		>
	</div>

	<!-- A 12-step wizard with no progress indicator leaves you counting in your head. -->
	<div class="bg-muted mb-6 h-1.5 overflow-hidden rounded-full">
		<div
			class="bg-primary h-full w-full origin-left rounded-full transition-transform duration-300"
			style="transform: scaleX({(index + 1) / data_keys.length})"
		></div>
	</div>

	<div class="flex flex-col gap-6 sm:flex-row sm:items-start">
		<div
			class="border-border bg-card mx-auto w-40 shrink-0 rounded-xl border p-3 shadow-sm sm:mx-0"
		>
			<img src={image_url} alt="" class="w-full" />
		</div>

		<div class="grid min-w-0 flex-1 grid-cols-3 gap-3 sm:grid-cols-4">
			{#each Array.from(Array(item_count[data_keys[index]]).keys()) as key}
				{@const chosen = data[data_keys[index]] === key}
				<button
					type="button"
					class="border-border bg-card hover:border-primary/60 focus-visible:ring-ring rounded-lg border p-1 transition focus-visible:ring-2 focus-visible:outline-none
						{chosen ? 'ring-primary ring-2' : ''}"
					aria-pressed={chosen}
					onclick={() => {
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
						alt=""
						class="w-full"
						in:fade|global={{ duration: 100 }}
					/>
				</button>
			{/each}
		</div>
	</div>
</div>
{#if finished}
	<div
		class="fixed top-0 left-0 w-full h-full z-30 bg-black/90 flex justify-center flex-col"
		out:fade|global={{ duration: 200 }}
		in:fade|global={{ duration: 300 }}
	>
		<h1 class="m-auto text-4xl" in:fade|global={{ delay: 3500 }}>
			{$t('avatar_settings.thats_you')}
		</h1>
		<img
			class="m-auto w-1/2 h-1/2 z-20"
			src={get_image_url(data)}
			in:fly|global={{ delay: 500, duration: 4000, y: -500, easing: bounceOut }}
		/>
		<div class="m-auto grid grid-cols-2 gap-4" in:fade|global={{ delay: 3500 }}>
			<BrownButton
				onclick={() => {
					index = 0;
					finished = false;
				}}>{$t('avatar_settings.start_over')}</BrownButton
			>
			<BrownButton onclick={save_avatar} flex={true} disabled={save_finished === true}>
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
				onclick={() => {
					finished = false;
				}}>{$t('words.close')}</BrownButton
			>
		</div>
	</div>
{/if}
