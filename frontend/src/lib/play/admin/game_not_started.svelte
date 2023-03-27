<!--
- This Source Code Form is subject to the terms of the Mozilla Public
- License, v. 2.0. If a copy of the MPL was not distributed with this
- file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->
<script lang="ts">
	import AudioPlayer from '$lib/play/audio_player.svelte';
	import { getLocalization } from '$lib/i18n';

	export let game_pin: string;
	export let players;
	export let socket;

	export let cqc_code: string;
	const { t } = getLocalization();
	let play_music = false;

	if (cqc_code === 'null') {
		cqc_code = null;
	}

	const kick_player = (username: string) => {
		socket.emit('kick_player', { username: username });
		for (let i = 0; i < players.length; i++) {
			console.log(players[i].username, username);
			if (players[i].username === username) {
				players.splice(i, 1);
				break;
			}
		}
		players = players;
	};
	const color_map = {
		r: 'red',
		g: 'green',
		y: 'yellow',
		b: 'blue'
	};
</script>

<div class="w-full h-full">
	<AudioPlayer bind:play={play_music} />
	<div class="grid grid-cols-3 mt-12">
		<div class="flex justify-center">
			<p class="m-auto text-2xl">
				Join at <b>{window.location.host}/play</b> and enter <b>{game_pin}</b>.
			</p>
		</div>
		<img
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="block mx-auto w-1/2 dark:bg-white"
		/>
		{#if cqc_code}
			<div class="m-auto">
				<div class="flex-col flex justify-center">
					<p class="mx-auto">Join by entering the following code</p>
					<div class="flex flex-row gap-2 mx-auto">
						{#each cqc_code as c}
							<div class="flex flex-col">
								<p class="text-center">{c}</p>
								<span
									style="background-color: {color_map[
										c.toLowerCase()
									]}; width: 2rem; height: {c.toLowerCase() == c ? '2' : '4'}rem"
								/>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}
	</div>
	<p class="text-3xl text-center ">{$t('words.pin')}: {game_pin}</p>
	<div class="flex justify-center w-full mt-4">
		<ul class="list-disc pl-8">
			{#if players.length > 0}
				{#each players as player}
					<li>
						<span
							class="hover:line-through"
							on:click={() => {
								kick_player(player.username);
							}}>{player.username}</span
						>
						<!--					<button>{$t('words.kick')}</button>-->
					</li>
				{/each}
			{/if}
		</ul>
	</div>
	{#if players.length > 0}
		<div class="flex justify-center w-full mt-4">
			<button
				class="ml-4 admin-button"
				id="startGame"
				on:click={() => {
					socket.emit('start_game', '');
				}}
				>{$t('admin_page.start_game')}
			</button>
		</div>
	{/if}
</div>
