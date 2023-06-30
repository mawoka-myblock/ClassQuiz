<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { QuizData } from '$lib/quiz_types';
	import Hoverable from '$lib/view_quiz/Hoverable.svelte';
	import { createTippy } from 'svelte-tippy';

	export let quiz: QuizData;

	let FeedBackButtonsHovered = {
		dislike: false,
		like: false
	};
	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'top'
	});

	const complete_action = async (positive: boolean) => {
		const res = await fetch(`/api/v1/community/rate/${quiz.id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ type: positive ? 'LIKE' : 'DISLIKE' })
		});
		if (res.status === 409) {
			alert("You've already rated this quiz!");
			return;
		} else if (!res.ok) {
			return;
		}
		if (positive) {
			quiz.likes += 1;
		} else {
			quiz.dislikes += 1;
		}
	};
</script>

<div class="flex flex-col border-[#B07156] rounded border-2 p-2 gap-2">
	<div class="grid grid-cols-2 gap-2 group mx-auto">
		<Hoverable bind:hovering={FeedBackButtonsHovered.like}>
			<button
				class="bg-green-500 rounded-full h-10 w-10 transition"
				use:tippy={{ content: 'Like this quiz!' }}
				class:opacity-40={FeedBackButtonsHovered.dislike}
				on:click={() => complete_action(true)}
			>
				<!-- heroicons/thumb-up -->
				<svg
					class="inline-block h-6 w-6 align-middle text-black"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
					/>
				</svg>
			</button>
		</Hoverable>
		<Hoverable bind:hovering={FeedBackButtonsHovered.dislike}>
			<button
				class="rounded-full bg-red-500 h-10 w-10 transition"
				use:tippy={{ content: 'Dislike this quiz!' }}
				class:opacity-40={FeedBackButtonsHovered.like}
				on:click={() => complete_action(false)}
			>
				<!-- heroicons/thumb-down -->
				<svg
					class="inline-block h-6 w-6 align-middle text-black"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5"
					/>
				</svg>
			</button>
		</Hoverable>
		<span class="text-center">{quiz.likes}</span>
		<span class="text-center">{quiz.dislikes}</span>
	</div>
	<span class="w-full border-t-2 border-[#B07156]" />
	<div class="mx-auto grid grid-cols-2 gap-2">
		<div class="flex flex-col">
			<!-- heroicons/legacy-outline/Play -->
			<svg
				class="w-8 h-8"
				use:tippy={{ content: 'How often the quiz was started' }}
				aria-hidden="true"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
				<path
					d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
			<p class="mx-auto" use:tippy={{ content: 'How often the quiz was started' }}>
				{quiz.plays}
			</p>
		</div>
		<div class="flex flex-col">
			<!-- heroicons/legacy-outline/Eye -->
			<svg
				class="w-8 h-8 mx-auto"
				use:tippy={{ content: 'Quiz views' }}
				aria-hidden="true"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
				<path
					d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
			<p class="mx-auto" use:tippy={{ content: 'Quiz views' }}>{quiz.views}</p>
		</div>
	</div>
</div>
