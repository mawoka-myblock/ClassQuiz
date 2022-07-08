<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import LanguageToggle from './language-toggle.svelte';
</script>

<footer class="text-center text-white border-black">
	<div class="grid grid-cols-12 w-full pt-4 bg-gray-700 pb-2">
		<p class="col-start-2 col-end-12 text-center w-full">
			Made with ❤️ by
			<a
				href="https://mawoka.eu?utm_source=ClassQuiz&utm_medium=footer"
				target="_blank"
				class="hover:underline bg-clip-text text-transparent bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f]"
				>Mawoka</a
			>
			and with the help of
			<a
				href="/docs/attribution"
				class="underline text-blue-300 hover:text-blue-500 transition">others</a
			>.
			<br />
			If you find this useful, please consider
			<a
				href="https://mawoka.eu/donate"
				target="_blank"
				class="underline text-blue-300 hover:text-blue-500 transition">Donating</a
			>.
			<a
				href="https://mawoka.eu/donate"
				target="_blank"
				class="underline text-blue-300 hover:text-blue-500 transition"
				>More details are here.</a
			>
		</p>
		<div class="self-end flex flex-col items-center min-h-full h-full">
			<div class="my-auto mr-16">
				<LanguageToggle />
			</div>
		</div>
	</div>
	<!-- to-[#8dc63f]-->
	<span
		class="w-full h-0.5 bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f] block bg-animated"
	/>

	<div class="flex justify-center bg-gray-700">
		<p class="text-gray-400 text-center">
			<i>Kahoot! and the K! logo are trademarks of Kahoot! AS</i>
		</p>
	</div>
</footer>

<style>
	.bg-animated {
		background-size: 30% 30%;

		-webkit-animation: ColorRunner 13s ease infinite;
		-moz-animation: ColorRunner 13s ease infinite;
		-o-animation: ColorRunner 13s ease infinite;
		animation: ColorRunner 13s ease infinite;
	}

	@-webkit-keyframes ColorRunner {
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

	@-moz-keyframes ColorRunner {
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

	@-o-keyframes ColorRunner {
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

	@keyframes ColorRunner {
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
