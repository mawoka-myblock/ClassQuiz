<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import Editor from '$lib/quiztivity/editor.svelte';
	import SharesPopover from '$lib/quiztivity/shares_popover.svelte';
	import { goto } from '$app/navigation';

	export let data: PageData;

	let saving = false;

	let quiztivity = data.quiztivity;
	let shares_menu_open = false;

	const save_quiztivity = async () => {
		saving = true;
		const stringification = JSON.stringify(quiztivity);

		const res = await fetch(`/api/v1/quiztivity/${quiztivity.id}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: stringification
		});
		if (res.ok) {
			await goto('/dashboard');
		} else {
			alert("Couldn't save");
		}
		saving = false;
	};
</script>

<div class="h-full">
	<Editor bind:data={quiztivity} on:save={save_quiztivity} bind:saving />
</div>

{#if shares_menu_open}
	<SharesPopover id={quiztivity.id} bind:open={shares_menu_open} />
{/if}
