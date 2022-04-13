<script lang="ts">
	/*
	import AdminOverviewScreenshot from '$lib/assets/landing/admin_overview.png';
	import SelectScreenshot from '$lib/assets/landing/select.webp';
	import ResultsScreenshot from '$lib/assets/landing/results.webp';
	import SolutionScreenshot from '$lib/assets/landing/solution.webp';
	*/
	import SelectMockup from '$lib/assets/landing/select-mockup.webp';
	import ResultsMockup from '$lib/assets/landing/results-mockup.webp';
	import SolutionMockup from '$lib/assets/landing/solution-mockup.webp';
	import ImportSelectMockup from '$lib/assets/landing/import-select-mockup.webp';
	import OverviewMockup from '$lib/assets/landing/overview-mockup.webp';

	let teacherTab = false;
</script>

<div class="grid grid-cols-1 overflow-hidden h-fit">
	{#if teacherTab}
		<div class="h-fit">
			<!--			<h1 class='text-5xl marck-script text-center pt-4'>Teacher</h1>-->

			<div class="grid lg:grid-cols-2 grow pt-4 transition ease-in-out">
				<h1 class="text-center text-3xl marck-script">1: Create or Import</h1>
				<h1 class="text-center text-3xl marck-script hidden lg:block">
					2: See all your quizzes
				</h1>
				<!--				<h1 class='text-center text-3xl marck-script'>3: See how many were right or wrong</h1>-->

				<div class="flex justify-center">
					<img src={ImportSelectMockup} class="w-4/6 align-top" alt="Select answer" />
				</div>
				<h1 class="text-center text-3xl marck-script lg:hidden block">
					2: See all your quizzes
				</h1>
				<div class="flex justify-center">
					<img
						src={OverviewMockup}
						class="w-4/6 align-top"
						alt="See right and wrong solutions"
					/>
				</div>
				<!--				<div class='flex justify-center'>-->
				<!--					<img-->
				<!--						src={ResultsMockup}-->
				<!--						class='max-h-80 align-top'-->
				<!--						alt='See results in comparison with other players'-->
				<!--					/>-->
				<!--				</div>-->
			</div>
		</div>
	{:else}
		<div class="h-fit">
			<!--			<h1 class='text-5xl marck-script text-center pt-4'>Student</h1>-->
			<div class="grid lg:grid-cols-3 grow pt-4 transition ease-in-out">
				<h1 class="text-center text-3xl marck-script">1: Answer</h1>
				<h1 class="text-center text-3xl marck-script lg:block hidden">
					2: See what was right or wrong
				</h1>
				<h1 class="text-center text-3xl marck-script lg:block hidden">
					3: See how many were right or wrong
				</h1>

				<div class="flex justify-center">
					<img src={SelectMockup} class="w-4/6 align-top" alt="Select answer" />
				</div>
				<h1 class="text-center text-3xl marck-script lg:hidden block">
					3: See how many were right or wrong
				</h1>
				<div class="flex justify-center">
					<div class="flex justify-center">
						<img
							src={SolutionMockup}
							class="w-4/6 align-top"
							alt="See right and wrong solutions"
						/>
					</div>
					<h1 class="text-center text-3xl marck-script lg:hidden block">
						3: See how many were right or wrong
					</h1>
					<div class="flex justify-center">
						<img
							src={ResultsMockup}
							class="w-4/6 align-top"
							alt="See results in comparison with other players"
						/>
					</div>
				</div>
			</div>
		</div>
	{/if}
	<div class="w-full h-fit pt-4">
		<div class="flex justify-center">
			<div class="flex justify-evenly lg:w-2/6">
				{#if teacherTab}
					<button
						class="border border-blue-600 p-2 border-2 rounded hover:bg-gray-700 text-2xl"
						on:click={() => {
							teacherTab = true;
						}}
						>Teacher's site
					</button>
				{:else}
					<button
						class="border border-black p-2 border-2 rounded hover:bg-gray-700 text-base"
						class:border-black={!teacherTab}
						class:text-base={!teacherTab}
						on:click={() => {
							teacherTab = true;
						}}
						>Teacher's site
					</button>
				{/if}
				<button
					class="border border-black p-2 border-2 rounded hover:bg-gray-700"
					class:border-blue-600={!teacherTab}
					class:text-2xl={!teacherTab}
					on:click={() => {
						teacherTab = false;
					}}
					>Student's site
				</button>
			</div>
		</div>
	</div>
</div>
