<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';

	export let current_slide_index: number;
	export let question_count: number;

	const { t } = getLocalization();
</script>

<div class="mt-auto h-[7vh] bg-opacity-50 bg-black shadow-2xl flex justify-between">
	<div class="my-auto justify-start ml-4">
		<BrownButton
			disabled={current_slide_index < 1}
			on:click={() => {
				current_slide_index -= 1;
			}}>{$t('words.back')}</BrownButton
		>
	</div>
	<div class="my-auto">
		{current_slide_index + 1}/{question_count}
	</div>
	<div class="my-auto justify-end mr-4">
		<BrownButton
			disabled={current_slide_index === 1}
			on:click={() => {
				current_slide_index += 1;
			}}>{$t('words.next')}</BrownButton
		>
	</div>
</div>
