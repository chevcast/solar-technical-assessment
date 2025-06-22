<script lang="ts">
	import GoogleMap from "$lib/components/GoogleMap.svelte";
	import LoadingIndicator from "$lib/components/LoadingIndicator.svelte";
	import { onMount } from "svelte";
	import { slide } from "svelte/transition";

	// Two-way bound state for our latitude and longitude.
	let latLng = $state<google.maps.LatLngLiteral>();
	// Derived state for formatted latitude and longitude values.
	let lat = $derived(latLng?.lat.toFixed(5));
	let lng = $derived(latLng?.lng.toFixed(5));
	// State to hold the optimal pitch and azimuth values.
	let optimalValues = $state<{
		pitch: number;
		azimuth: number;
		insolation_kwh_m2: {
			annual: number;
		};
	}>();
	// State to hold the user-provided offset angle.
	let offsetAngle = $state<number>(0);

	// State to track if the offset or coordinates have been modified.
	let offsetDirty = $state(false);
	let coordsDirty = $state(false);

	// Effect to fetch the optimal tilt values whenever latLng our
	// offsetAngle changes.
	$effect(() => {
		if (latLng) {
			fetch(`/api/optimal-tilt`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					lat: latLng.lat,
					lng: latLng.lng,
					offsetAngle
				})
			})
				.then((response) => response.json())
				.then((data) => {
					optimalValues = data;
					offsetDirty = false;
					coordsDirty = false;
				})
				.catch((error) => {
					console.error(error);
				});
		}
	});

	// Debounced timeout for offset keypress handling to void excessive API calls.
	let offsetKeypressTimeout: NodeJS.Timeout | null = null;
	const handleOffsetKeypress = (event: KeyboardEvent) => {
		offsetDirty = true;
		const offsetInput = event.currentTarget as HTMLInputElement;
		if (offsetKeypressTimeout) clearTimeout(offsetKeypressTimeout);
		if (event.key === "Enter") {
			offsetAngle = offsetInput.value ? parseFloat(offsetInput.value) : 0;
		} else {
			offsetKeypressTimeout = setTimeout(() => {
				offsetAngle = offsetInput.value ? parseFloat(offsetInput.value) : 0;
			}, 750);
		}
	};

	const setCoords = () => {
		if (!lat || !lng) throw new Error("setCoords was called without valid lat or lng");
		latLng = {
			lat: parseFloat(lat),
			lng: parseFloat(lng)
		};
	};

	// Debounced timeout for offset keypress handling to void excessive API calls.
	let coordsKeypressTimeout: NodeJS.Timeout | null = null;
	const handleCoordsKeypress = (event: KeyboardEvent) => {
		coordsDirty = true;
		if (coordsKeypressTimeout) clearTimeout(coordsKeypressTimeout);
		if (event.key === "Enter") {
			setCoords();
		} else {
			coordsKeypressTimeout = setTimeout(() => {
				setCoords();
			}, 2000);
		}
	};

	// On mount, attempt to get the user's current geolocation.
	// This only works on localhost or over HTTPS.
	onMount(() => {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(
				(position) => {
					latLng = {
						lat: position.coords.latitude,
						lng: position.coords.longitude
					};
				},
				(error) => {
					console.error(error.message);
					latLng = {
						lat: 37.7749,
						lng: -122.4194
					};
				}
			);
		}
	});
</script>

<div class="relative flex h-screen w-screen flex-col">
	<!-- Toolbar header with latitude and longitude inputs -->
	<div
		class="z-10 flex w-full items-center justify-center bg-sky-700 p-4 text-xl text-white shadow-lg shadow-sky-950"
	>
		<label for="latInput" aria-label="Latitude">Lat</label>
		<input
			id="latInput"
			onkeypress={handleCoordsKeypress}
			bind:value={lat}
			type="text"
			placeholder="latitude"
			class={[
				"mr-4 ml-1 w-30 rounded-lg bg-white px-2 py-1 text-sky-950 shadow shadow-sky-950",
				coordsDirty ? "bg-yellow-100" : "bg-white"
			]}
		/>
		<label for="lngInput" aria-label="Longitude">Lng</label>
		<input
			id="lngInput"
			onkeypress={handleCoordsKeypress}
			bind:value={lng}
			type="text"
			placeholder="longitude"
			class={[
				"mr-2 ml-1 w-30 rounded-lg bg-white px-2 py-1 text-sky-950 shadow shadow-sky-950",
				coordsDirty ? "bg-yellow-100" : "bg-white"
			]}
		/>
		{#if coordsDirty}
			<LoadingIndicator class="size-8 text-yellow-100" />
		{/if}
	</div>

	<!-- Optimal panel mount display -->
	{#if optimalValues && !coordsDirty}
		<div
			transition:slide={{ duration: 300 }}
			class="z-5 bg-sky-700 p-4 text-xl text-white shadow-lg shadow-sky-950 md:absolute md:top-30 md:right-15 md:w-1/3 md:rounded-2xl md:border-2 md:border-sky-300"
		>
			<h1 class="mb-5 text-center text-lg font-bold md:text-xl">Optimal Panel Mount</h1>
			<div class="mb-5 flex items-center">
				<label for="offsetInput" aria-label="Offset Angle" class="mr-4 w-50 text-right"
					>Offset Angle</label
				>
				<input
					id="offsetInput"
					class={[
						"mr-2 w-15 rounded-lg px-2 py-1 text-center text-sky-950 shadow shadow-sky-950",
						offsetDirty ? "bg-yellow-100" : "bg-white"
					]}
					value={offsetAngle}
					onkeypress={handleOffsetKeypress}
				/>
				{#if offsetDirty}
					<LoadingIndicator class="size-8 text-yellow-100" />
				{/if}
			</div>
			<div class="mb-4 flex items-center">
				<div class="mr-4 w-50 text-right">Pitch</div>
				<div class="rounded-lg bg-sky-300 px-2 font-bold text-sky-950">{optimalValues.pitch}</div>
			</div>
			<div class="mb-4 flex items-center">
				<div class="mr-4 w-50 text-right">Azimuth</div>
				<div class="rounded-lg bg-sky-300 px-2 font-bold text-sky-950">
					{optimalValues.azimuth}
				</div>
			</div>
			<div class="flex items-center">
				<div class="mr-4 w-50 text-right">Insolation Intensity</div>
				<div class="rounded-lg bg-sky-300 px-2 font-bold text-sky-950">
					{optimalValues.insolation_kwh_m2.annual} kWh/m²/yr
				</div>
			</div>
		</div>
	{/if}

	<!-- Google Map component with the current latLng and azimuth -->
	<div class="flex-1">
		<GoogleMap bind:latLng azimuth={optimalValues?.azimuth} />
	</div>
</div>
