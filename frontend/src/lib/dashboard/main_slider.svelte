<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { Swiper, SwiperSlide } from 'swiper/svelte';
	import 'swiper/css';
	import 'swiper/css/pagination';
	import 'swiper/css/navigation';
	import { Pagination, EffectCoverflow, Keyboard, Mousewheel, Navigation } from 'swiper';
	import { QuizQuestionType } from '$lib/quiz_types.js';
	import { getLocalization } from '../i18n';
	import { alertModal } from '../stores';

	const { t } = getLocalization();
	export let quizzes;

	const startGame = async (id: string): Promise<void> => {
		let res;
		if (window.confirm('Do you want to enable the captcha for players?')) {
			res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=True`, {
				method: 'POST'
			});
		} else {
			res = await fetch(`/api/v1/quiz/start/${id}?captcha_enabled=False`, {
				method: 'POST'
			});
		}

		if (res.status !== 200) {
			alertModal.set({
				open: true,
				title: 'Start failed',
				body: `Failed to start game, ${await res.text()}`
			});
			alertModal.subscribe((_) => {
				window.location.assign('/account/login?returnTo=/dashboard');
			});
		}
		const data = await res.json();
		// eslint-disable-next-line no-undef
		plausible('Started Game', { props: { quiz_id: id } });
		window.location.assign(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
	};
	/*
	const deleteQuiz = async (to_delete: string) => {
		if (!confirm('Do you really want to delete this quiz?')) {
			return;
		}
		await fetch(`/api/v1/quiz/delete/${to_delete}`, {
			method: 'DELETE'
		});
		window.location.reload();
	};

	 */
</script>

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
		{#each quizzes as quiz}
			<SwiperSlide>
				<div class="flex justify-center pt-4 px-4">
					<a href="/edit?quiz_id={quiz.id}" class="text-3xl">{quiz.title}</a>
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
								<div class="grid grid-cols-6 h-full">
									<p
										style="writing-mode: vertical-lr"
										class="text-center h-full text-xl p-2"
									>
										{quiz.title}
									</p>
									<p class="text-center col-start-2 col-end-6">
										{quiz.description}
									</p>
									<div class="flex justify-end">
										<p
											style="writing-mode: sideways-lr"
											class="text-center text-xl p-2"
										>
											{quiz.title}
										</p>
									</div>
								</div>
								<p class="text-center">{quiz.questions.length} Questions</p>
								<div class="flex justify-center mt-8">
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
								<div class="flex justify-center pb-20 pt-8">
									<div class="flex flex-col gap-4">
										<a
											href="/edit?quiz_id={quiz.id}"
											class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
											>Edit</a
										>
										<button
											on:click={() => {
												startGame(quiz.id);
											}}
											class="px-4 py-2 leading-5 text-black dark:text-white transition-colors duration-200 transform bg-gray-50 dark:bg-gray-700 rounded text-center hover:bg-gray-300 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-gray-600"
										>
											Start
										</button>
									</div>
								</div>
								<div class="flex justify-center" />
							</SwiperSlide>
							{#each quiz.questions as question}
								<SwiperSlide>
									<div class="h-full">
										<h5 class="text-center text-2xl">{question.question}</h5>
										{#if question.image}
											<div
												class="flex justify-center align-middle items-center"
											>
												<div class="h-[30vh] m-auto w-auto">
													<img
														class="max-h-full max-w-full  block"
														src={question.image}
														alt="Not provided"
													/>
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
