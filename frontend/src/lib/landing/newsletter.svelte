<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let open: boolean;

	const closeThing = () => {
		open = false;
		localStorage.setItem('newsletter', 'closed');
	};
</script>

<form method="post" action="https://newsletter.mawoka.eu/subscription/form" class="bg-transparent">
	<div class="absolute top-1 right-1">
		<button type="button" on:click={closeThing}>
			<svg
				class="w-6 h-6"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		</button>
	</div>
	<div>
		<h3 class="text-lg font-semibold">ClassQuiz-Newsletter</h3>
		<input type="hidden" name="nonce" />
		<p>
			<input
				type="email"
				name="email"
				required
				placeholder="E-mail"
				class="m-0.5 border-b-2 border-gray-300 rounded-lg p-0.5 outline-none focus:outline-gray-400 bg-transparent"
			/>
		</p>
		<p>
			<input
				type="text"
				name="name"
				placeholder="Name (optional)"
				class="m-0.5 border-b-2 border-gray-300 rounded-lg p-0.5 outline-none focus:outline-gray-400 bg-transparent"
			/>
		</p>

		<p class="hidden">
			<input
				id="fec55"
				type="checkbox"
				name="l"
				checked
				value="fec5595e-9af1-497a-b7eb-1edd7ad2e21c"
			/>
			<label for="fec55">ClassQuiz-News</label>
		</p>
		<div class="bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f] w-fit rounded-lg">
			<button
				type="submit"
				class="m-0.5 bg-opacity-70 bg-white rounded-lg py-0.5 px-1 text-black"
				>Subscribe!
			</button>
		</div>
	</div>
</form>
