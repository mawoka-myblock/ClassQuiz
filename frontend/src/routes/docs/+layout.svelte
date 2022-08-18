<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
