<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import LanguageToggle from './language-toggle.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
</script>

<footer class="text-center text-white border-black w-screen">
	<div class="grid grid-cols-12 w-full pt-4 bg-gray-700 pb-2">
		<p class="col-start-3 col-end-11 text-center w-full">
			{@html $t('footer.self_ads', {
				mawoka_link:
					'<a href="https://mawoka.eu?utm_source=ClassQuiz&utm_medium=footer" target="_blank" class="hover:underline bg-clip-text text-transparent bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f]">Mawoka</a>',
				others_link: `<a href="/docs/attribution" class="underline text-blue-300 hover:text-blue-500 transition">${$t(
					'words.other',
					{ count: 2 }
				)}</a>`,
				interpolation: { escapeValue: false }
			})}
			<br />

			{@html $t('footer.donate', {
				donate_link: `<a href='https://mawoka.eu/donate' target='_blank' class='underline text-blue-300 hover:text-blue-500 transition'>${$t(
					'words.donating'
				)}</a>`,
				interpolation: { escapeValue: false }
			})}
			<a
				href="https://mawoka.eu/donate"
				target="_blank"
				class="underline text-blue-300 hover:text-blue-500 transition"
				>{$t('footer.more_details_here')}.</a
			>
		</p>
		<div
			class="flex flex-col items-center min-h-full h-full md:block hidden col-start-11 col-end-12"
		>
			<div class="my-auto mr-16">
				<LanguageToggle />
			</div>
		</div>
	</div>
	<div class="md:hidden block">
		<div class="self-end flex justify-center min-h-full h-full bg-gray-700 pb-2 md:pb-0">
			<div class="m-auto md:invisible visible">
				<LanguageToggle />
			</div>
		</div>
	</div>

	<!-- to-[#8dc63f]-->
	<span class="w-full h-0.5 bg-gradient-to-r from-[#009444] via-[#39b54a] to-[#8dc63f] block" />

	<div class="flex justify-center bg-gray-700">
		<p class="text-gray-400 text-center">
			<i>Kahoot! and the K! logo are trademarks of Kahoot! AS</i>
		</p>
	</div>
</footer>

<!--
<style>
	.bg-animated {
		background-size: 100% 100%;

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
-->
