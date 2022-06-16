<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';

	export let data: EditorData;
</script>

<div class="w-full h-full p-20">
	<div class="rounded-lg bg-white w-full h-full border-gray-500">
		<div class="h-fit bg-gray-300 rounded-t-lg">
			<div class="flex align-middle p-4 gap-3">
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-red-400 transition"
				/>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-yellow-400 transition"
				/>
				<span
					class="inline-block bg-gray-600 w-4 h-4 rounded-full hover:bg-green-400 transition"
				/>
			</div>
		</div>
		<div>
			<div class="flex justify-center pt-10 w-full">
				<input
					type="text"
					bind:value={data.title}
					class="p-3 rounded-lg border-gray-500 border text-center w-1/3"
				/>
			</div>
		</div>
	</div>
</div>
