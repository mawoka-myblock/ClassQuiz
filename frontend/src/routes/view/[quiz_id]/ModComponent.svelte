<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';

	export let autoReturn = false;
	export let quiz_id: string;
	let mod_rating: number | undefined;

	const submit = async () => {
		const res = await fetch(`/api/v1/moderation/rating/set/${quiz_id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ rating: mod_rating })
		});
		if (res.ok && autoReturn) {
			window.history.back();
		}
		if (!res.ok) {
			alert('Setting rating failed');
		}
	};
</script>

<div class="rounded border-2 border-[#B07156] flex flex-col w-fit gap-2 p-2">
	<div class:opacity-50={mod_rating !== null && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = null)}>Not Checked</BrownButton>
	</div>
	<div class:opacity-50={mod_rating !== 0 && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = 0)}>Ok</BrownButton>
	</div>
	<div class:opacity-50={mod_rating !== 1 && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = 1)}>Attention</BrownButton>
	</div>
	<div class:opacity-50={mod_rating !== 2 && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = 2)}>NFSW</BrownButton>
	</div>
	<div class:opacity-50={mod_rating !== 3 && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = 3)}>Plausibility Checked</BrownButton>
	</div>
	<div class:opacity-50={mod_rating !== 4 && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = 4)}>Fact Checked</BrownButton>
	</div>
	<div class:opacity-50={mod_rating !== 5 && mod_rating !== undefined} class="transition">
		<BrownButton on:click={() => (mod_rating = 5)}>Exceptional</BrownButton>
	</div>
	<GrayButton on:click={submit} disabled={mod_rating === undefined}>Submit</GrayButton>
</div>
