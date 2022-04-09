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

	navbarVisible.set(true);
</script>

<slot />
