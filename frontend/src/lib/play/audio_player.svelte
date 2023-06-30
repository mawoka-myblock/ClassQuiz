<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Audio1 from '$lib/assets/music/1-128.mp3';

	export let play = false;
	let volume = 100;

	const audio = new Audio(Audio1);
	const control_audio = (play_audio: boolean) => {
		if (play_audio) {
			audio.play();
			audio.loop = true;
		} else {
			audio.pause();
		}
	};
	$: audio.volume = volume / 100;
	$: control_audio(play);
</script>

<div class="fixed top-0 left-0">
	{#if play}
		<button
			on:click={() => {
				play = false;
			}}
		>
			<!-- heroicons/volume-up -->
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
					d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
				/>
			</svg>
		</button>
	{:else}
		<button
			on:click={() => {
				play = true;
			}}
		>
			<!-- heroicons/volume-off -->
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
					d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
					clip-rule="evenodd"
				/>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
				/>
			</svg>
		</button>
	{/if}
	<input type="range" class="vertical_input" bind:value={volume} min="0" max="100" />
</div>
