<script lang="ts">
	import Footer from '$lib/footer.svelte';
</script>

<div class="min-h-screen flex flex-col">
	<slot />
</div>
<div class="pt-4">
	<Footer />
</div>
