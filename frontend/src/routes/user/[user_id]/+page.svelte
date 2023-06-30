<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { getLocalization } from '$lib/i18n';
	import { onMount } from 'svelte';
	import { createTippy } from 'svelte-tippy';
	import { signedIn } from '$lib/stores';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';

	const { t } = getLocalization();
	// import { DateTime } from 'luxon';
	let start_game = null;

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'right'
	});

	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			start_game = null;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
	export let data: PageData;
</script>

<svelte:head>
	<title>ClassQuiz - {data.user.username ? `@${data.user.username}` : 'User not found'}</title>
</svelte:head>

<div class="h-full">
	<div class="grid grid-cols-6 h-full">
		<div class="pl-2">
			{#if data.user.username === undefined}
				<h2 class="text-4xl text-center p-4">{$t('public_user_page.user_not_found')}</h2>
			{:else}
				<div class="flex justify-center">
					<img src={`/api/v1/users/avatar/${data.user.id}`} alt="profile" />
				</div>
				<h2 class="text-3xl text-center">
					@{data.user.username}
				</h2>
				<p class="italic text-center">
					{$t('public_user_page.joined_on', {
						date: new Date(data.user.created_at).toLocaleDateString()
					})}
				</p>
			{/if}
		</div>
		<div
			class="col-start-2 col-end-7 border-l border-black h-full p-4 overflow-y-scroll flex flex-col gap-4"
		>
			{#if data.quizzes.length === 0}
				<p class="text-center text-4xl">{$t('public_user_page.no_original_quizzes')}</p>
			{:else}
				{#each data.quizzes as quiz}
					<div
						class="rounded-lg border-2 border-black hover:outline transition-all outline-[#B07156] -outline-offset-2 outline-8"
					>
						<div class="grid grid-cols-6 h-[25vh]">
							<!--						<p
														style='writing-mode: vertical-lr'
														class='text-center h-full text-xl p-2'
													>
														{@html quiz.title}
													</p>-->
							<div class="col-start-2 col-end-6">
								<h3 class="text-center text-2xl">{@html quiz.title}</h3>
								<p class="text-center">
									{@html quiz.description}
								</p>
								{#if quiz.cover_image}
									<div class="flex justify-center align-middle items-center">
										<div class="h-[20vh] m-auto w-auto max-h-[18vh]">
											<img
												class="max-h-full max-w-full block"
												src="/api/v1/storage/download/{quiz.cover_image}"
												alt="Not provided"
												loading="lazy"
											/>
										</div>
									</div>
								{/if}
							</div>

							<!--						<div class='flex justify-end'>
														<p
															style='writing-mode: sideways-lr'
															class='text-center text-xl p-2'
														>
															{@html quiz.title}
														</p>
													</div>-->
						</div>
						<div class="flex justify-center">
							<a href="/view/{quiz.id}" class="action-button w-1/6"
								>{$t('words.view')}</a
							>
						</div>
						<div class="flex justify-center pb-10 pt-8">
							<div class="grid grid-cols-2 gap-3 w-1/3">
								{#if $signedIn}
									<button
										on:click={() => {
											start_game = quiz.id;
										}}
										class="action-button"
									>
										{$t('words.start')}
									</button>
									<a
										href="/api/v1/eximport/{quiz.id}"
										aria-label="Download the quiz"
										class="flex justify-center px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
										><!-- heroicons/download -->
										<svg
											class="w-5 h-5"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
											xmlns="http://www.w3.org/2000/svg"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
											/>
										</svg>
									</a>
								{:else}
									<div
										use:tippy={{
											content: 'You need be signed in to start a game.'
										}}
										class="w-full"
									>
										<button
											on:click={() => {
												start_game = quiz.id;
											}}
											disabled
											class="action-button w-full"
										>
											{$t('words.start')}
										</button>
									</div>
									<div
										use:tippy={{
											content: 'You need be signed in to download a game.'
										}}
										class="w-full"
									>
										<button
											disabled
											class="action-button w-full flex justify-center"
										>
											<svg
												class="w-5 h-5"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
												xmlns="http://www.w3.org/2000/svg"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
												/>
											</svg>
										</button>
									</div>
								{/if}
							</div>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>
</div>
{#if start_game !== null}
	<StartGamePopup bind:quiz_id={start_game} />
{/if}
