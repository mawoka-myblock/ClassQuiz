<script>
	import '../app.css';
	import Navbar from '$lib/navbar.svelte';
	import { navbarVisible } from '$lib/stores.ts';
	import * as Sentry from '@sentry/browser';
	import { BrowserTracing } from '@sentry/tracing';

	if (import.meta.env.VITE_SENTRY !== null) {
		Sentry.init({
			dsn: import.meta.env.VITE_SENTRY,
			integrations: [new BrowserTracing()],

			// Set tracesSampleRate to 1.0 to capture 100%
			// of transactions for performance monitoring.
			// We recommend adjusting this value in production
			tracesSampleRate: 0.5
		});
	}

</script>

{#if $navbarVisible}
	<Navbar />
	<div class='pt-16 h-screen'>
		<slot />
	</div>
{:else}
	<slot />
{/if}

<style lang='scss'>
  :global(body) {
    // height: 100%;
    // width: 100%;
    background: linear-gradient(to right, #009444, #39b54a, #8dc63f) repeat-y;
    background-size: cover;
    /*background: linear-gradient(-225deg, #231557 0%, #44107A 29%, #FF1361 67%, #FFF800 100%); */
    /*background: linear-gradient(-225deg, #22E1FF 0%, #1D8FE1 48%, #625EB1 100%); */
    color: beige;

    // background-size: 400% 400%;

    //animation: background_animation 5s ease infinite;
  }

  @keyframes background_animation {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }
</style>
