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
	import Footer from '$lib/footer.svelte';
	import { navbarVisible } from '$lib/stores';

	navbarVisible.set(true);
</script>

<div class="min-h-screen flex flex-col">
	<slot />
</div>
<div class="pt-4">
	<Footer />
</div>
