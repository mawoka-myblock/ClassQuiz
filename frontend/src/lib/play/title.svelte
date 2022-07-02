<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	export let title: string;
	export let description: string;
</script>

<div class="flex flex-col justify-center w-screen h-screen">
	<h1 class="text-7xl text-center">{title}</h1>
	<p class="text-3xl pt-8 text-center">{description}</p>
</div>
