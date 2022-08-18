<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts" context="module">
	throw new Error(
		'@migration task: Check code was safely removed (https://github.com/sveltejs/kit/discussions/5774#discussioncomment-3292722)'
	);

	// import { signedIn } from '$lib/stores';

	// export async function load({ session }) {
	// 	if (session.authenticated) {
	// 		signedIn.set(true);
	// 	}
	// 	return {};
	// }
</script>

<script lang="ts">
	import { navbarVisible } from '$lib/stores';

	navbarVisible.set(true);
</script>

<slot />
