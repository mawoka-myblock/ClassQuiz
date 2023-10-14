<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// import { alertModal } from '$lib/stores';
	import { captcha_enabled } from '$lib/config';
	import StartGameBackground from './start_game_background.svg';
	import { fade } from 'svelte/transition';
	import Spinner from '$lib/Spinner.svelte';
	import { onMount } from 'svelte';
	import { createTippy } from 'svelte-tippy';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	export let quiz_id;
	let captcha_selected = false;
	let selected_game_mode = 'kahoot';
	let loading = false;
	let custom_field = '';
	let cqcs_enabled = false;
	let randomized_answers = false;

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top-start',
		allowHTML: true
	});

	onMount(() => {
		const ls_data = localStorage.getItem('custom_field');
		custom_field = ls_data ? ls_data : '';
	});

	const start_game = async (id: string) => {
		let res;
		loading = true;
		localStorage.setItem('custom_field', custom_field);
		const cqcs_enabled_parsed = cqcs_enabled ? 'True' : 'False';
		const randomized_answers_parsed = randomized_answers ? 'True' : 'False';
		if (captcha_enabled && captcha_selected) {
			res = await fetch(
				`/api/v1/quiz/start/${id}?captcha_enabled=True&game_mode=${selected_game_mode}&custom_field=${custom_field}&cqcs_enabled=${cqcs_enabled_parsed}`,
				{
					method: 'POST'
				}
			);
		} else {
			res = await fetch(
				`/api/v1/quiz/start/${id}?captcha_enabled=False&game_mode=${selected_game_mode}&custom_field=${custom_field}&cqcs_enabled=${cqcs_enabled_parsed}&randomize_answers=${randomized_answers_parsed}`,
				{
					method: 'POST'
				}
			);
		}
		if (res.status !== 200) {
			/*			alertModal.set({
				open: true,
				title: 'Start failed',
				body: `Failed to start game, ${await res.text()}`
			});*/
			/*alertModal.subscribe((_) => {
				window.location.assign('/account/login?returnTo=/dashboard');
			});*/
			alert('Starting game failed');
			window.location.assign('/account/login?returnTo=/dashboard');
		} else {
			const data = await res.json();
			// eslint-disable-next-line no-undef
			plausible('Started Game', { props: { quiz_id: id, game_id: data.game_id } });
			window.location.assign(
				`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1&cqc_code=${data.cqc_code}`
			);
		}
	};

	const on_parent_click = (e: Event) => {
		if (e.target !== e.currentTarget) {
			return;
		}
		quiz_id = null;
	};
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			quiz_id = null;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
</script>

<div
	class="fixed top-0 left-0 flex justify-center w-screen h-screen bg-black bg-opacity-60 z-50 text-black"
	transition:fade={{ duration: 100 }}
	on:click={on_parent_click}
>
	<div
		class="w-5/6 h-5/6 bg-black m-auto rounded-lg shadow-lg p-4 flex flex-col"
		style="background-image: url({StartGameBackground}); background-color: #DFDBE5;"
	>
		<div class="flex justify-center w-full">
			<label
				for="large-toggle"
				class="inline-flex relative items-center cursor-pointer"
				class:pointer-events-none={!captcha_enabled}
				class:opacity-50={!captcha_enabled}
			>
				<input
					type="checkbox"
					bind:checked={captcha_selected}
					id="large-toggle"
					class="sr-only peer"
				/>
				<span
					class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
				/>
				<span class="ml-3 text-sm font-medium text-gray-900"
					>Captcha {captcha_selected ? 'enabled' : 'disabled'}</span
				>
			</label>
		</div>
		{#if captcha_selected}
			<div class="flex justify-center mt-2" in:fade>
				<p class="w-1/3">
					{$t('start_game.captcha_message')}
				</p>
				<!-- Todo: Add translation  -->
			</div>
		{/if}

		<div class="grid grid-cols-2 gap-8 my-auto">
			<div
				class="rounded-lg bg-white shadow-lg cursor-pointer transition-all p-2"
				class:opacity-50={selected_game_mode !== 'kahoot'}
				on:click={() => {
					selected_game_mode = 'kahoot';
				}}
			>
				<h2 class="text-center text-2xl">{$t('words.normal')}</h2>
				<p>
					{$t('start_game.normal_mode_description')}
				</p>
			</div>
			<div
				class="rounded-lg bg-white shadow-lg cursor-pointer transition-all p-2"
				class:opacity-50={selected_game_mode !== 'normal'}
				on:click={() => {
					selected_game_mode = 'normal';
				}}
			>
				<h2 class="text-center text-2xl">{$t('start_game.old_school_mode')}</h2>
				<p>
					{$t('start_game.old_school_mode_description')}
				</p>
			</div>
		</div>
		<div class="flex justify-center items-center my-auto">
			<label class="mr-4">{$t('result_page.custom_field')}</label>
			<input
				bind:value={custom_field}
				class="rounded-lg p-2 outline-none placeholder:italic"
				placeholder="Phone Number or Email"
			/>
		</div>
		<div class="flex justify-center w-full my-auto">
			<label for="cqc-toggle" class="inline-flex relative items-center cursor-pointer">
				<input
					type="checkbox"
					bind:checked={cqcs_enabled}
					id="cqc-toggle"
					class="sr-only peer"
				/>
				<span
					class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
				/>
				<span class="ml-3 text-sm font-medium text-gray-900"
					><a
						href="/controller"
						target="_blank"
						use:tippy={{
							content:
								'ClassQuizControllers are small physical devices to play ClassQuiz. Click to learn more.'
						}}
						class="decoration-dashed underline cursor-help">ClassQuizControllers</a
					>
					are {cqcs_enabled ? 'enabled' : 'disabled'}</span
				>
			</label>
		</div>
		<div class="flex justify-center w-full my-auto">
			<label
				for="randomized-answers-toggle"
				class="inline-flex relative items-center cursor-pointer"
			>
				<input
					type="checkbox"
					bind:checked={randomized_answers}
					id="randomized-answers-toggle"
					class="sr-only peer"
				/>
				<span
					class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
				/>
				<span class="ml-3 text-sm font-medium text-gray-900"> Randomize answers</span>
			</label>
		</div>

		<button
			class="mt-auto mx-auto bg-green-500 p-4 rounded-lg shadow-lg hover:bg-green-400 transition-all marck-script text-2xl"
			on:click={() => {
				start_game(quiz_id);
			}}
		>
			{#if loading}
				<Spinner my_20={false} />
			{:else}
				{$t('start_game.start_game')}
			{/if}
		</button>
	</div>
</div>
