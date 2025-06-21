<script lang="ts">
	import { onMount } from "svelte";
	import { googleLoader } from "$lib/utils/googleLoader";

	let { latLng = $bindable<google.maps.LatLng>(), ...props } = $props();

	let mapDiv: HTMLDivElement;

	let marker = $state<google.maps.marker.AdvancedMarkerElement>();
	let map = $state<google.maps.Map>();

	const setMarker = async (position: google.maps.LatLng) => {
		if (!map) throw new Error("Map is not initialized");
		const { AdvancedMarkerElement } = (await google.maps.importLibrary(
			"marker"
		)) as google.maps.MarkerLibrary;
		latLng.lat = position.lat();
		latLng.lng = position.lng();
		if (marker) {
			marker.position = position;
		} else {
			marker = new AdvancedMarkerElement({ map, position });
		}
		const zoom = map.getZoom();
		if (zoom && zoom < 20) {
			map.setZoom(20);
		}
		map.panTo(latLng);
	};

	$effect(() => {
		if (latLng && map && window.google) {
			const coords = new google.maps.LatLng(latLng);
			setMarker(coords);
		}
	});

	const initMap = async () => {
		const { Map } = (await google.maps.importLibrary("maps")) as google.maps.MapsLibrary;

		const map = new Map(mapDiv, {
			clickableIcons: false,
			center: latLng, // Default: SF
			zoom: 20,
			mapId: crypto.randomUUID(),
			mapTypeId: "satellite",
			tilt: 0
		});

		map.addListener("click", (event: google.maps.MapMouseEvent) => {
			// console.log("Clicked coordinates:", event.latLng?.toJSON());
			const position = event.latLng!;
			setMarker(position);
		});

		return map;
	};

	onMount(async () => {
		await googleLoader();
		map = await initMap();
	});
</script>

<div id="google-map" class="h-full w-full" {...props} bind:this={mapDiv}></div>
