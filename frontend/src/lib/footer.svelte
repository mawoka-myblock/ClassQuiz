<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
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
					'<a href="https://mawoka.eu?utm_source=ClassQuiz&utm_medium=footer" target="_blank" class="underline text-blue-300 hover:text-blue-500 transition">Mawoka</a>',
				others_link: `<a href='/docs/attribution' class='underline text-blue-300 hover:text-blue-500 transition'>${$t(
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

	<div class="bg-gray-700">
		<p>
			Consider following
			<svg
				class="inline-block h-4 w-4"
				fill="#6364FF"
				role="img"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				><title> Mastodon</title>
				<path
					d="M23.268 5.313c-.35-2.578-2.617-4.61-5.304-5.004C17.51.242 15.792 0 11.813 0h-.03c-3.98 0-4.835.242-5.288.309C3.882.692 1.496 2.518.917 5.127.64 6.412.61 7.837.661 9.143c.074 1.874.088 3.745.26 5.611.118 1.24.325 2.47.62 3.68.55 2.237 2.777 4.098 4.96 4.857 2.336.792 4.849.923 7.256.38.265-.061.527-.132.786-.213.585-.184 1.27-.39 1.774-.753a.057.057 0 0 0 .023-.043v-1.809a.052.052 0 0 0-.02-.041.053.053 0 0 0-.046-.01 20.282 20.282 0 0 1-4.709.545c-2.73 0-3.463-1.284-3.674-1.818a5.593 5.593 0 0 1-.319-1.433.053.053 0 0 1 .066-.054c1.517.363 3.072.546 4.632.546.376 0 .75 0 1.125-.01 1.57-.044 3.224-.124 4.768-.422.038-.008.077-.015.11-.024 2.435-.464 4.753-1.92 4.989-5.604.008-.145.03-1.52.03-1.67.002-.512.167-3.63-.024-5.545zm-3.748 9.195h-2.561V8.29c0-1.309-.55-1.976-1.67-1.976-1.23 0-1.846.79-1.846 2.35v3.403h-2.546V8.663c0-1.56-.617-2.35-1.848-2.35-1.112 0-1.668.668-1.67 1.977v6.218H4.822V8.102c0-1.31.337-2.35 1.011-3.12.696-.77 1.608-1.164 2.74-1.164 1.311 0 2.302.5 2.962 1.498l.638 1.06.638-1.06c.66-.999 1.65-1.498 2.96-1.498 1.13 0 2.043.395 2.74 1.164.675.77 1.012 1.81 1.012 3.12z"
				/>
			</svg>
			<a
				href="https://fosstodon.org/@classquiz"
				rel="me"
				class="underline text-blue-300 hover:text-blue-500 transition"
				>@classquiz@fosstodon.org</a
			> for updates!
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
