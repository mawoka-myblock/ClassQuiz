<script lang="ts" context="module">
	import { signedIn } from '$lib/stores';

	export async function load({ session }) {
		if (session.authenticated) {
			signedIn.set(true);
		}
		return {};
	}
</script>

<script lang="ts">
	import { navbarVisible } from '$lib/stores';
	import { getLocalization } from '$lib/i18n';
	import Footer from '$lib/footer.svelte';

	import LandingPromo from '$lib/landing/landing-promo.svelte';

	const { t } = getLocalization();

	navbarVisible.set(true);

	interface StatsData {
		quiz_count: number;
		user_count: number;
	}

	const getStats = async (): Promise<StatsData> => {
		const response = await fetch('/api/v1/stats/combined');
		return await response.json();
	};
</script>

<svelte:head>
	<title>ClassQuiz - {$t('index_page.meta.title')}</title>
	<meta name="description" content={$t('index_page.meta.description')} />
</svelte:head>

<div class="min-h-screen flex flex-col">
	<section>
		<div class="pt-12 text-center">
			<h1 class="sm:text-8xl text-6xl mt-6 marck-script">ClassQuiz</h1>
			<p class="text-xl mt-4">{$t('index_page.slogan')}</p>
		</div>
	</section>

	<section id="stats">
		<div class="text-center pt-48 snap-y">
			<h1 class="sm:text-6xl text-4xl">{$t('words.stats')}</h1>
			<p class="text-xl pt-4">
				{#await getStats() then stats}
					There are already <span class="underline">{stats.user_count}</span> users and
					<!-- TODO: Add translation -->
					<span class="underline">{stats.quiz_count}</span> quizzes on ClassQuiz.
				{/await}
			</p>
		</div>
	</section>

	<section class="py-8">
		<h1 class="sm:text-6xl text-4xl text-center">Screenshots</h1>
		<div>
			<LandingPromo />
		</div>
	</section>

	<!--
	<section>
		<h1 class='sm:text-6xl text-4xl text-center'>Testimonials</h1>
		{#await import('$lib/landing/testimonials.svelte') then testimonials}
			<svelte:component this={testimonials.default} />
		{/await}
	</section>
	-->
	<section id="features" class="mt-8">
		<div class="text-center snap-y">
			<h1 class="sm:text-6xl text-4xl">{$t('words.features')}</h1>
			<p class="text-xl pt-4">
				{$t('index_page.features_description.1')}
				<br />
				{$t('index_page.features_description.2')}
			</p>
		</div>
	</section>
</div>

<Footer />
