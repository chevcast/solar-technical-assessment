<script lang="ts">
	import GoogleMap from "$lib/components/GoogleMap.svelte";
	import { onMount, untrack } from "svelte";
	import { slide } from "svelte/transition";

	let latLng = $state<google.maps.LatLngLiteral>();
	let lat = $derived(latLng?.lat.toFixed(5));
	let lng = $derived(latLng?.lng.toFixed(5));
	let optimalValues = $state<{
		pitch: number;
		azimuth: number;
	}>();
	let offsetAngle = $state<number>(0);

	$effect(() => {
		if (latLng) {
			optimalValues = undefined;
			fetch(`/api/optimal-tilt`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					lat: latLng.lat,
					lng: latLng.lng,
					offsetAngle: untrack(() => offsetAngle)
				})
			})
				.then((response) => response.json())
				.then((data) => {
					optimalValues = data;
				})
				.catch((error) => {
					console.error(error);
				});
		}
	});

	const setCoords = () => {
		if (!lat || !lng) throw new Error("setCoords was called without valid lat or lng");
		latLng = {
			lat: parseFloat(lat),
			lng: parseFloat(lng)
		};
	};

	let keyPressTimeout: NodeJS.Timeout | null = null;
	const handleKeyPress = (event: KeyboardEvent) => {
		if (keyPressTimeout) clearTimeout(keyPressTimeout);
		if (event.key === "Enter") {
			setCoords();
		} else {
			keyPressTimeout = setTimeout(() => {
				setCoords();
			}, 2000);
		}
	};

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
	<div
		class="z-10 flex w-full items-center justify-center bg-sky-700 p-4 text-xl text-white shadow-lg shadow-sky-950"
	>
		<label for="latInput" aria-label="Latitude">Lat</label>
		<input
			id="latInput"
			onkeypress={handleKeyPress}
			bind:value={lat}
			type="text"
			placeholder="latitude"
			class="mr-4 ml-1 w-30 rounded-lg bg-white px-2 py-1 text-sky-950 shadow shadow-sky-950"
		/>
		<label for="lngInput" aria-label="Longitude">Lng</label>
		<input
			id="lngInput"
			onkeypress={handleKeyPress}
			bind:value={lng}
			type="text"
			placeholder="longitude"
			class="mr-4 ml-1 w-30 rounded-lg bg-white px-2 py-1 text-sky-950 shadow shadow-sky-950"
		/>
	</div>
	{#if optimalValues}
		<div
			transition:slide={{ duration: 300 }}
			class="z-5 bg-sky-700 p-4 text-xl text-white shadow-lg shadow-sky-950 md:absolute md:top-30 md:right-15 md:w-1/3 md:rounded-2xl md:border-2 md:border-sky-300"
		>
			<h1 class="mb-5 text-center text-lg font-bold md:text-xl">Optimal Panel Tilt</h1>
			<div class="mb-5 flex items-center">
				<label for="offsetInput" aria-label="Offset Angle" class="mr-4 w-30 text-right"
					>Offset Angle</label
				>
				<input
					id="offsetInput"
					class="w-15 rounded-lg bg-white px-2 py-1 text-center text-sky-950 shadow shadow-sky-950"
					bind:value={offsetAngle}
				/>
			</div>
			<div class="mb-4 flex items-center">
				<div class="mr-4 w-30 text-right">Pitch</div>
				<div class="rounded-lg bg-sky-300 px-2 font-bold text-sky-950">{optimalValues.pitch}</div>
			</div>
			<div class="mb-2 flex items-center">
				<div class="mr-4 w-30 text-right">Azimuth</div>
				<div class="rounded-lg bg-sky-300 px-2 font-bold text-sky-950">
					{optimalValues.azimuth}
				</div>
			</div>
		</div>
	{/if}
	<div class="flex-1">
		<GoogleMap bind:latLng />
	</div>
</div>
