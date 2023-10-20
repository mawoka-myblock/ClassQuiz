<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<!--
<script context='module' lang='ts'>
	export const prerender = true;
	export const load = async ({}) => {
		return {};
		const languages = [
			{
				code: 'de',
				name: 'Deutsch',
				flag: '🇩🇪'
			},
			{
				code: 'en',
				name: 'English',
				flag: '🇺🇲'
			},
			{
				code: 'tr',
				name: 'Türkçe',
				flag: '🇹🇷'
			},
			{
				code: 'fr',
				name: 'Français',
				flag: '🇫🇷'
			}
		];
		let final_arr = [];
		const set_percents = async () => {
			for (const lang of languages) {
				const res = await fetch(`https://translate.mawoka.eu/api/translations/classquiz/frontend/${lang.code}/?format=json`);
				const json = await res.json();
				console.log(json);
				// return Math.floor(json.translated_percent);
				final_arr.push({ ...lang, percent: json.translated_percent });
			}
		};
		await set_percents();
		return {
			slot: {
				final_arr
			}
		};
	};
</script>
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	export let languages: Array<{
		flag: string;
		name: string;
		code: string;
	}> = [
		{
			code: 'de',
			name: 'Deutsch',
			flag: '🇩🇪'
		},
		{
			code: 'en',
			name: 'English',
			flag: '🇺🇲'
		},
		{
			code: 'tr',
			name: 'Türkçe',
			flag: '🇹🇷'
		},
		{
			code: 'fr',
			name: 'Français',
			flag: '🇫🇷'
		},
		{
			code: 'id',
			name: 'Bahasa Indonesia',
			flag: '🇮🇩'
		},
		{
			code: 'ca',
			name: 'Català',
			flag: '🇪🇸'
		},
		{
			code: 'it',
			name: 'Italiano',
			flag: '🇮🇹'
		},
		{
			code: 'es',
			name: 'Español',
			flag: '🇪🇸'
		},
		{
			code: 'nb_NO',
			name: 'Norsk',
			flag: '🇳🇴'
		},
		{
			code: 'zh_Hant',
			name: 'Chinese (traditional)',
			flag: '🇨🇳'
		},
		{
			code: 'pl',
			name: 'Polski',
			flag: '🇵🇱'
		},
		{
			code: 'pt',
			name: 'Português',
			flag: '🇵🇹'
		},
		{
			code: 'uk',
			name: 'Українська',
			flag: '🇺🇦'
		},
		{
			code: 'nl',
			name: 'Nederlands',
			flag: '🇳🇱'
		},
		{
			code: 'hu',
			name: 'Magyar',
			flag: '🇭🇺'
		},
		{
			code: 'vi',
			name: 'tiếng Việt',
			flag: '🇻🇳'
		}
	];
	const get_selected_language = (): string => {
		return localStorage.getItem('language');
	};
	let selected_language;
	onMount(() => {
		selected_language = get_selected_language();
	});

	const set_language = (code: string): void => {
		if (browser) {
			localStorage.setItem('language', code);
			window.location.reload();
		}
	};
</script>

<div>
	<select
		bind:value={selected_language}
		on:change={() => {
			set_language(selected_language);
		}}
		class="p-2 rounded-lg bg-gray-800 focus:ring-2 ring-blue-600 text-white"
		aria-label="Language-Selector"
	>
		{#each languages as lang}
			<option value={lang.code}>{lang.flag} {lang.name} </option>
		{/each}
	</select>
</div>
