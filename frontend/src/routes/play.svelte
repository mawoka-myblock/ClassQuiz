<script context='module' lang='ts'>
	export async function load({ url }) {
		const token = url.searchParams.get('token');
		return {
			props: {
				game_pin: token === null ? '' : token
			}
		};
	}
</script>

<script lang='ts'>
	import { socket } from '$lib/socket';

	export let game_pin: string;
	let game_pin_valid = false;
	console.log(game_pin);


	const setUsername = (username: string) => {
		console.log(username);
	};
	const setGamePin = (game_pin: string) => {
		socket.emit()
	};

	$: console.log(game_pin.length);

</script>

<div>
	{#if game_pin === "" || game_pin.length <= 7 || !game_pin_valid}
		<div class='flex flex-col justify-center align-center w-screen h-screen'>
			<form on:submit|preventDefault={setGamePin} class='flex-col flex justify-center align-center mx-auto'>
				<h1 class='text-lg text-center'>Game Pin</h1>
				<input class='border border-amber-800 self-center text-center' bind:value={game_pin} maxlength='8'>
				<br>
				<button class='bg-amber-800 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded'
						type='submit'>
					Submit
				</button>
			</form>
		</div>

	{:else}
		<div class='flex flex-col justify-center align-center w-screen h-screen'>
			<form on:submit|preventDefault={setUsername} class='flex-col flex justify-center align-center mx-auto'>
				<h1 class='text-lg text-center'>Username</h1>
				<input class='border border-amber-800'>
				<button class='bg-amber-800 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded' type='submit'>
					Submit
				</button>
			</form>
		</div>
	{/if}
</div>