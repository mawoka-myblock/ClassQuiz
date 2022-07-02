<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts" context="module">
	export async function load({ url }) {
		const error = url.searchParams.get('error');
		return {
			props: {
				error
			}
		};
	}
</script>

<script lang="ts">
	export let error: string;
</script>

<div>
	<div class="flex justify-center w-full">
		<h1 class="text-6xl">Error authenticating</h1>
	</div>

	<div class="flex justify-center w-full pt-10">
		<p>
			{#if error === 'email'}
				GitHub didn't respond with an email-address. Are you sure your email-address is
				verified?
			{:else}
				There was an error authenticating you. Are you sure you've got an email? Is the
				Email verified?
			{/if}
		</p>
	</div>
	<div class="flex justify-center w-full pt-10">
		<a
			href="/account/login"
			class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
		>
			Go back to login-page
		</a>
	</div>
	<div class="flex justify-center w-full pt-10">
		<p>
			If the error persists, please open an <a
				href="https://github.com/mawoka-myblock/ClassQuiz/issues/new?assignees=&labels=&template=Bug_report.md"
				class="underline transition hover:text-blue-300">issue on GitHub</a
			>.
		</p>
	</div>
</div>
