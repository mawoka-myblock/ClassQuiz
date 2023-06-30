<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<!--
By Flowbite, but changed: https://flowbite.com/docs/components/modal/#default-modal
-->
<script lang="ts">
	export let title: string;
	export let body: string;
	export let open: boolean;
	console.log(open, title, body);
	open = true;
</script>

<!-- Main modal -->
{#if open}
	<div tabindex="-1" class="overflow-y-auto overflow-x-hidden md:inset-0 lg:w-2/6 w-5/6">
		<div class="relative p-4 w-full max-w-2xl h-full md:h-auto">
			<!-- Modal content -->
			<div class="relative bg-white rounded-lg shadow dark:bg-gray-700">
				<!-- Modal header -->
				<div
					class="flex justify-between items-start p-4 rounded-t border-b dark:border-gray-600"
				>
					<h3 class="text-xl font-semibold text-gray-900 dark:text-white">
						{title}
					</h3>
					<button
						type="button"
						class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-600 dark:hover:text-white"
						on:click={() => {
							open = false;
						}}
					>
						<svg
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
				<!-- Modal body -->
				<div class="p-6 space-y-6">
					<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
						{body}
					</p>
				</div>
				<!-- Modal footer -->
				<div
					class="flex items-center p-6 space-x-2 rounded-b border-t border-gray-200 dark:border-gray-600"
				>
					<button
						data-modal-toggle="defaultModal"
						type="button"
						on:click={() => {
							open = false;
						}}
						class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
					>
						Close
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
