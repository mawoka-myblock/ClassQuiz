<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import type { Data } from '$lib/quiztivity/types';
	import Editor from '$lib/quiztivity/editor.svelte';
	import { goto } from '$app/navigation';

	let data: Data = { pages: [], id: undefined, title: '' };
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
