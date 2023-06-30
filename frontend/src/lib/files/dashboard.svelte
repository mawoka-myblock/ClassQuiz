<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
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
