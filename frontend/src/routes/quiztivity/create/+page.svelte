<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Data } from '$lib/quiztivity/types';
	import Editor from '$lib/quiztivity/editor.svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let title = $page.url.searchParams.get('title');
	title ??= '';

	let data: Data = { pages: [], id: undefined, title };
	let saving = false;

	const save_quiztivity = async () => {
		saving = true;
		console.log(data);
		const stringification = JSON.stringify(data);
		console.log(stringification);

		const res = await fetch('/api/v1/quiztivity/create', {
			method: 'POST',
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
	<Editor bind:data on:save={save_quiztivity} bind:saving />
</div>
