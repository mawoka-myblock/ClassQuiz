<script lang="ts">
	import { onMount } from 'svelte';

	export let image_element;

	let number_of_spans;
	let number_of_cols;
	let data_arr;
	const box_size = 50;
	export let seed: string;
	export let width: number;
	export let height: number;

	function mulberry32(a: any) {
		return function () {
			a |= 0;
			a = (a + 0x6d2b79f5) | 0;
			var t = Math.imul(a ^ (a >>> 15), 1 | a);
			t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
	}

	const random_gen = mulberry32(seed);

	const make_one_thing_transparent = () => {
		console.log('make on thing transpartern');
		let random_el_index = Math.floor(random_gen() * data_arr.length);
		let random_el = data_arr[random_el_index];
		if (random_el === false) {
			make_one_thing_transparent();
			return;
		}
		data_arr[random_el_index] = false;
		setTimeout(make_one_thing_transparent, 500);
	};

	const on_image_load = () => {
		console.log(seed);
		console.log('mounted!!!');
		console.log(width, height);
		number_of_cols = Math.ceil(width / box_size);
		number_of_spans = Math.ceil(width / box_size) * Math.ceil(height / box_size);
		console.log(number_of_spans);
		data_arr = Array.apply(null, Array(number_of_spans)).map(() => true);
		make_one_thing_transparent();
		console.log('Finished init');
	};
	onMount(on_image_load);
</script>

<div>
	<div class="relative">
		<!--<img
			src={image_url}
			alt='lol'
			bind:this={image_element}
			style='{image_styles}'
			on:load={on_image_load}
		/>
		-->
		<slot />
		<div class="absolute top-0 right-0 w-full h-full">
			{#if number_of_spans}
				<div
					class="grid overflow-hidden"
					style="grid-template-columns: repeat({number_of_cols}, minmax(0, 1fr))"
				>
					{#each { length: number_of_spans } as _, i}
						<span
							class="ransition duration-700"
							style="width: {box_size}px; height: {box_size}px;"
							class:bg-transparent={!data_arr[i]}
							class:bg-red-400={data_arr[i]}
						/>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
