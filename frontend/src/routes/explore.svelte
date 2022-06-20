<script context="module" lang="ts">
	import { signedIn } from '$lib/stores';

	export async function load({ session }) {
		if (session.authenticated) {
			signedIn.set(true);
		}
		return {};
	}
</script>

<script lang="ts">
	import SearchCard from '$lib/search-card.svelte';
	const getData = async () => {
		const response = await fetch('/api/v1/search/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				q: '*',
				sort: ['created_at:desc']
			})
		});
		return await response.json();
	};
</script>

<svelte:head>
	<title>ClassQuiz - Explore</title>
</svelte:head>

{#await getData()}
	<svg class="h-8 w-8 animate-spin mx-auto my-20" viewBox="3 3 18 18">
		<path
			class="fill-black"
			d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
		/>
		<path
			class="fill-blue-100"
			d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"
		/>
	</svg>
{:then quizzes}
	<div class="grid lg:grid-cols-3 grid-cols-1">
		{#each quizzes.hits as quiz}
			<SearchCard {quiz} />
		{/each}
	</div>
{/await}
