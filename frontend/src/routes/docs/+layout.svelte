<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

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
