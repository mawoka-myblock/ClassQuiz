<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<script lang="ts">
	import Spinner from '$lib/Spinner.svelte';

	export let files: {
		id: string;
		uploaded_at: string;
		mime_type?: string;
		hash?: string;
		size: number;
		deleted_at?: string;
		alt_text?: string;
		filename?: string;
		thumbhash?: string;
		server?: string;
		quizzes: { id: string }[];
		quiztivities: { id: string }[];
	}[];

	const get_files = async () => {
		const res = await fetch('/api/v1/storage/list');
		files = await res.json();
	};
	if (!files) {
		get_files();
	}
</script>

{#if files}{:else}
	<Spinner />
{/if}
