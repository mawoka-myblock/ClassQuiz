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
	import WebPOpenGraph from '$lib/assets/landing/opengraph-home.webp';
	import JpgOpenGraph from '$lib/assets/landing/opengraph-home.jpg';

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
	<title>ClassQuiz - Home</title>
	<meta
		name="description"
		content="ClassQuiz is a quiz-application like KAHOOT!, but open-source. You can create quizzes and play them remotely with other people."
	/>

	<meta property="og:url" content="https://classquiz.de/" />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="ClassQuiz - {$t('index_page.meta.title')}" />
	<meta
		property="og:description"
		content="ClassQuiz is a quiz-application like KAHOOT!, but open-source. You can create quizzes and play them remotely with other people."
	/>
	<meta property="og:image" content={JpgOpenGraph} />

	<meta name="twitter:card" content="summary_large_image" />
	<meta property="twitter:domain" content="classquiz.de" />
	<meta property="twitter:url" content="https://classquiz.de/" />
	<meta name="twitter:title" content="ClassQuiz - {$t('index_page.meta.title')}" />
	<meta
		name="twitter:description"
		content="ClassQuiz is a quiz-application like KAHOOT!, but open-source. You can create quizzes and play them remotely with other people."
	/>
	<meta name="twitter:image" content={WebPOpenGraph} />
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
					{$t('index_page.stats', {
						user_count: stats.user_count,
						quiz_count: stats.quiz_count
					})}
				{/await}
			</p>
		</div>
	</section>

	<section class="py-8">
		<h1 class="sm:text-6xl text-4xl text-center">{$t('words.screenshot', { count: 2 })}</h1>
		<div>
			<LandingPromo />
		</div>
	</section>

	<section>
		<h1 class="sm:text-6xl text-4xl text-center">Testimonials</h1>
		{#await import('$lib/landing/testimonials.svelte') then testimonials}
			<svelte:component this={testimonials.default} />
		{/await}
	</section>
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
