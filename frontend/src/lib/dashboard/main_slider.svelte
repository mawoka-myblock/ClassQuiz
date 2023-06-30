<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { Swiper, SwiperSlide } from 'swiper/svelte';
	import 'swiper/css';
	import 'swiper/css/pagination';
	import 'swiper/css/navigation';
	import { Pagination, EffectCoverflow, Keyboard, Mousewheel, Navigation } from 'swiper';
	import { fly } from 'svelte/transition';
	import { QuizQuestionType } from '$lib/quiz_types.js';
	import { getLocalization } from '$lib/i18n';
	import StartGamePopup from './start_game.svelte';
	// import { onMount } from 'svelte';
	import viewport from './useViewportAction.js';
	import Spinner from '$lib/Spinner.svelte';
	import GrayButton from '$lib/components/buttons/gray.svelte';

	let copy_toast_open = false;
	let start_game = null;
	const { t } = getLocalization();
	export let quizzes = [];

	const deleteQuiz = async (to_delete: string) => {
		if (!confirm('Do you really want to delete this quiz?')) {
			return;
		}
		await fetch(`/api/v1/quiz/delete/${to_delete}`, {
			method: 'DELETE'
		});
		window.location.reload();
	};
	let visibleImages = Array.from(Array(quizzes.length), () => []);

	const copy_id = (quiz_id: string) => {
		navigator.clipboard.writeText(quiz_id);
		copy_toast_open = true;
		setTimeout(() => {
			copy_toast_open = false;
		}, 2000);
	};

	let game_in_lobby: { game_pin: string; game_id: string; quiz_title: string } | undefined =
		undefined;

	const get_game_in_lobby_fn = async () => {
		const res = await fetch('/api/v1/remote/game_waiting');
		console.log('Fetched.');
		if (res.ok) {
			game_in_lobby = await res.json();
		}
	};
	// onMount(() => {
	// 	document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	// });

	get_game_in_lobby_fn();
</script>

{#if copy_toast_open || game_in_lobby}
	<div class="fixed w-screen top-10 z-50 flex justify-center" transition:fly={{ y: -100 }}>
		<div
			class="flex items-center p-4 w-full max-w-xs text-gray-500 bg-white rounded-lg shadow dark:text-gray-400 dark:bg-gray-800"
			role="alert"
		>
			<div class="ml-3 text-sm font-normal">
				{#if copy_toast_open}ID copied to clipboard!
				{:else}A game is currently in the lobby. Click <a
						class="underline"
						href="/remote?game_pin={game_in_lobby.game_pin}&game_id={game_in_lobby.game_id}"
						>here</a
					> to join as a remote.
				{/if}
			</div>
			<button
				type="button"
				class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700"
				data-dismiss-target="#toast-default"
				aria-label="Close"
				on:click={() => {
					copy_toast_open = false;
					game_in_lobby = undefined;
				}}
			>
				<span class="sr-only">Close</span>
				<svg
					aria-hidden="true"
					class="w-5 h-5"
					fill="currentColor"
					viewBox="0 0 20 20"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						fill-rule="evenodd"
						d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>
		</div>
	</div>
{/if}

<div class="w-screen p-8">
	<Swiper
		grabCursor={true}
		effect={'coverflow'}
		modules={[EffectCoverflow, Pagination, Mousewheel, Navigation]}
		navigation={true}
		slidesPerView={1}
		mousewheel={true}
		centeredSlides={true}
		coverflowEffect={{
			rotate: 50,
			stretch: 0,
			depth: 100,
			modifier: 1,
			slideShadows: false
		}}
		pagination={{
			clickable: true
		}}
	>
		{#each quizzes as quiz, i}
			<SwiperSlide>
				<div class="flex justify-center pt-4 px-4">
					<a href="/edit?quiz_id={quiz.id}" class="text-3xl">{@html quiz.title}</a>
				</div>
				<div class="flex justify-center p-10 h-full">
					<div class="border-2 border-black rounded-lg w-5/6">
						<Swiper
							pagination={{
								clickable: true
							}}
							keyboard={{ enabled: true }}
							grabCursor={true}
							navigation={true}
							modules={[Pagination, Keyboard, Navigation]}
						>
							<SwiperSlide>
								<div class="grid grid-cols-6 h-[25vh]">
									<p
										style="writing-mode: vertical-lr"
										class="text-center h-full text-xl p-2"
									>
										{@html quiz.title}
									</p>
									<div class="col-start-2 col-end-6">
										<p class="text-center">
											{@html quiz.description}
										</p>
										{#if quiz.cover_image}
											<div
												class="flex justify-center align-middle items-center"
											>
												<div class="h-[20vh] m-auto w-auto">
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

									<div class="flex justify-end">
										<p
											style="writing-mode: sideways-lr"
											class="text-center text-xl p-2"
										>
											{@html quiz.title}
										</p>
									</div>
								</div>

								<p class="text-center">
									{quiz.questions.length}
									{$t('words.question', { count: quiz.questions.length })}
								</p>

								<div class="flex justify-center mt-4">
									{#if quiz.public}
										<svg
											class="w-8 h-8 inline-block"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
											xmlns="http://www.w3.org/2000/svg"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
											/>
										</svg>
										<span>{$t('words.public')}</span>
									{:else}
										<svg
											class="w-8 h-8 inline-block"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
											xmlns="http://www.w3.org/2000/svg"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
											/>
										</svg>
										<span>{$t('words.private')}</span>
									{/if}
								</div>
								<div class="flex justify-center pb-10 pt-8">
									<div class="grid grid-cols-2 gap-3 w-1/3">
										<GrayButton href="/edit?quiz_id={quiz.id}"
											>{$t('words.edit')}</GrayButton
										>
										<GrayButton
											on:click={() => {
												start_game = quiz.id;
											}}
										>
											{$t('words.start')}
										</GrayButton>
										<GrayButton
											on:click={() => {
												deleteQuiz(quiz.id);
											}}
											flex={true}
										>
											<!-- heroicons/trash -->
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
													d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
												/>
											</svg>
										</GrayButton>
										<GrayButton href="/api/v1/eximport/{quiz.id}" flex={true}
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
										</GrayButton>
									</div>
								</div>
								<div class="flex justify-center">
									<p
										class="text-sm font-mono select-all cursor-pointer"
										on:click={() => {
											copy_id(quiz.id);
										}}
									>
										{quiz.id}
									</p>
								</div>
							</SwiperSlide>
							{#each quiz.questions as question, q}
								<SwiperSlide>
									<div class="h-full">
										<h5 class="text-center text-2xl">
											{@html question.question}
										</h5>
										{#if question.image}
											<div
												use:viewport
												on:enterViewport={() => {
													visibleImages[i][q] = true;
												}}
												on:exitViewport={() => {
													visibleImages[i][q] = false;
												}}
												class="flex justify-center align-middle items-center"
											>
												<div class="h-[30vh] m-auto w-auto">
													{#if visibleImages?.[i]?.[q]}
														<img
															class="max-h-full max-w-full block"
															src="/api/v1/storage/download/{question.image}"
															alt="Not provided"
														/>
													{/if}
												</div>
											</div>
										{/if}
										<p
											class="m-1 flex flex-row gap-2 flex-nowrap whitespace-nowrap w-full justify-center"
										>
											<svg
												class="w-8 h-8 inline-block"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
												xmlns="http://www.w3.org/2000/svg"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
											<span class="text-lg">{question.time}s</span>
										</p>
										{#if question.type === QuizQuestionType.ABCD || question.type === undefined}
											<div class="grid grid-cols-2 gap-4 m-4 p-6">
												{#each question.answers as answer, index_answer}
													<div
														class="p-1 rounded-lg py-4"
														class:bg-green-500={answer.right}
														class:bg-red-500={!answer.right}
													>
														<h4 class="text-center">
															{answer.answer}
														</h4>
													</div>
												{/each}
											</div>
										{:else if question.type === QuizQuestionType.RANGE}
											<p class="m-1 text-center">
												All numbers between {question.answers.min_correct}
												and {question.answers.max_correct} are correct, where
												numbers between {question.answers.min} and {question
													.answers.max} can be selected.
											</p>
										{:else if question.type === QuizQuestionType.VOTING}
											<div class="grid grid-cols-2 gap-4 m-4 p-6">
												{#each question.answers as answer}
													<div
														class="p-1 rounded-lg py-4 dark:bg-gray-500 bg-gray-300"
													>
														<h4 class="text-center">
															{answer.answer}
														</h4>
													</div>
												{/each}
											</div>
										{:else if question.type === QuizQuestionType.ORDER}
											<ul class="flex flex-col gap-4 m-4 p-6">
												{#each question.answers as answer}
													<li
														class="p-1 rounded-lg py-3 dark:bg-gray-500 bg-gray-300"
													>
														<h4 class="text-center">
															{answer.answer}
														</h4>
													</li>
												{/each}
											</ul>
										{:else if question.type === QuizQuestionType.SLIDE}
											<div
												use:viewport
												on:enterViewport={() => {
													visibleImages[i][q] = true;
												}}
												on:exitViewport={() => {
													visibleImages[i][q] = false;
												}}
												class="flex justify-center align-middle items-center"
											>
												{#await import('$lib/play/admin/slide.svelte')}
													<Spinner my={false} />
												{:then c}
													<div class="max-h-[50%] max-w-[60%]">
														<svelte:component
															this={c.default}
															bind:question
														/>
													</div>
												{/await}
											</div>
										{/if}
									</div>
								</SwiperSlide>
							{/each}
						</Swiper>
					</div>
				</div>
			</SwiperSlide>
		{/each}
	</Swiper>
</div>

{#if start_game !== null}
	<StartGamePopup bind:quiz_id={start_game} />
{/if}
