<script lang="ts">
	/*	import AdminOverviewScreenshot from '$lib/assets/landing/admin_overview.png';
	import SelectScreenshot from '$lib/assets/landing/select.webp';
	import ResultsScreenshot from '$lib/assets/landing/results.webp';
	import SolutionScreenshot from '$lib/assets/landing/solution.webp';*/
	import SelectMockup from '$lib/assets/landing/select-mockup.webp';
	import ResultsMockup from '$lib/assets/landing/results-mockup.webp';
	import SolutionMockup from '$lib/assets/landing/solution-mockup.webp';
</script>

<div class="grid grid-cols-3 grow pt-4">
	<h1 class="text-center h-fit text-3xl marck-script">1: Answer</h1>
	<h1 class="text-center h-fit text-3xl marck-script">2: See what was right or wrong</h1>
	<h1 class="text-center h-fit text-3xl marck-script">3: See how many were right or wrong</h1>

	<div class="flex justify-center">
		<img src={SelectMockup} class="max-h-80" alt="Select answer" />
	</div>
	<div class="flex justify-center">
		<img src={SolutionMockup} class="max-h-80" alt="See right and wrong solutions" />
	</div>
	<div class="flex justify-center">
		<img
			src={ResultsMockup}
			class="max-h-80"
			alt="See results in comparison with other players"
		/>
	</div>
</div>
