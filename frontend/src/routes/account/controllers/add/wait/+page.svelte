<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import CodeDisplay from '$lib/components/controller/code.svelte';
	import Spinner from '$lib/Spinner.svelte';
	import { onMount } from 'svelte';

	export let data: PageData;
	let controller_seen = false;
	let check_tick = 0;
	let interval;

	const check_if_controller_was_seen = async () => {
		const res = await fetch(`/api/v1/box-controller/web/controller?id=${data.id}`);
		const json = await res.json();
		controller_seen = Boolean(json.first_seen);
		if (controller_seen) {
			clearInterval(interval);
		}
	};

	onMount(async () => {
		await check_if_controller_was_seen();
		interval = setInterval(async () => {
			check_tick += 1;
			if (check_tick === 5) {
				await check_if_controller_was_seen();
				check_tick = 0;
			}
		}, 1000);
	});
</script>

<div class="w-full h-full flex">
	<div class="m-auto flex flex-col">
		<div class="block">
			<CodeDisplay code={data.code} />
		</div>
		{#if controller_seen}
			<div class="mt-10">
				<p class="text-center">Controller set up successfully!</p>
			</div>
		{:else}
			<div class="mt-10 flex-col flex gap-2 justify-center">
				<p>Checking if controller has been connected in {5 - check_tick} seconds.</p>
				<Spinner my_20={false} />
			</div>
		{/if}
	</div>
</div>
