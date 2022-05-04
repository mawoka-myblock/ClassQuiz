<script>
	export let headerText;

	let expanded = false;
</script>

<div>
	<h3 class="bg-white dark:bg-slate-800 m-0">
		<button
			aria-expanded={expanded}
			on:click={() => (expanded = !expanded)}
			class="bg-white dark:bg-slate-800 flex justify-between w-full border-none m-0 p-2"
			>{headerText}
			<svg viewBox="0 0 20 20" fill="none" class="my-auto">
				<path class="vert" d="M10 1V19" stroke="black" stroke-width="2" />
				<path d="M1 10L19 10" stroke="black" stroke-width="2" />
			</svg>
		</button>
	</h3>

	<div class="border-b-1 border-gray-500" class:hidden={!expanded}>
		<slot />
	</div>
</div>

<style>
	/*	h3 {
		margin: 0;
	}

	button {
		background-color: var(--background, #fff);
		color: var(--gray-darkest, #282828);
		display: flex;
		justify-content: space-between;
		width: 100%;
		border: none;
		margin: 0;
		padding: 1em 0.5em;
	}*/
	button {
	}

	button[aria-expanded='true'] {
		border-bottom: 1px solid var(--gray-light, #eee);
	}

	button[aria-expanded='true'] .vert {
		display: none;
	}

	button:focus svg {
		outline: 2px solid;
	}

	svg {
		height: 0.7em;
		width: 0.7em;
	}
</style>
