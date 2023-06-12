<!--
- This Source Code Form is subject to the terms of the Mozilla Public
- License, v. 2.0. If a copy of the MPL was not distributed with this
- file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->
<script lang="ts">
	import Spinner from '$lib/Spinner.svelte';

	let uppyOpen = false;
	let edit_id = null;
	let selected_question = undefined;
	let data = { cover_image: undefined };

	$: {
		if (data.cover_image) {
			window.location.reload();
		}
	}
</script>

{#await import('$lib/editor/uploader.svelte')}
	<Spinner my_20={false} />
{:then c}
	<svelte:component
		this={c.default}
		bind:modalOpen={uppyOpen}
		bind:edit_id
		bind:data
		bind:selected_question
		video_upload={true}
		library_enabled={false}
	/>
{/await}
