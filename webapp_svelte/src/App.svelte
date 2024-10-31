<script>
	import LaneSwimTable from './components/LaneSwimTable.svelte';
</script>

<main>
	<!-- <h1>Welcome to the prototype LaneSwimTable for the Greater Ottawa Region</h1> -->
	<LaneSwimTable />
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #3700ff;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>