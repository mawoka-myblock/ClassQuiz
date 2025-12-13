<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Spinner from '$lib/Spinner.svelte';

	let uppyOpen = $state(false);
	let edit_id = $state(null);
	let selected_question = $state(undefined);
	let data = $state({ cover_image: undefined });

	$effect(() => {
		if (data.cover_image) {
			window.location.reload();
		}
	});
</script>

{#await import('$lib/editor/uploader.svelte')}
	<Spinner my_20={false} />
{:then c}
	<c.default
		bind:modalOpen={uppyOpen}
		bind:edit_id
		bind:data
		bind:selected_question
		video_upload={true}
		library_enabled={false}
	/>
{/await}
