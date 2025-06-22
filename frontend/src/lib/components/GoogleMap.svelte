<script lang="ts">
	import { onMount } from "svelte";
	import { googleLoader } from "$lib/utils/googleLoader";

	// Use two-way bindnig for latLng so this component and its parent can both react to changes.
	let { latLng = $bindable<google.maps.LatLng>(), azimuth, ...props } = $props();

	let mapDiv: HTMLDivElement;

	// Reative state for map objects.
	let marker = $state<google.maps.marker.AdvancedMarkerElement>();
	let direction = $state<google.maps.Polyline>();
	let map = $state<google.maps.Map>();

	// Calculate the destination point given a starting point, azimuth, and distance.
	const destPoint = (lat: number, lng: number, az: number, d = 50) => {
		const R = 6371000;
		const theta = (az * Math.PI) / 180;
		const delta = d / R;
		const phi1 = (lat * Math.PI) / 180;
		const lambda1 = (lng * Math.PI) / 180;
		const phi2 = Math.asin(
			Math.sin(phi1) * Math.cos(delta) + Math.cos(phi1) * Math.sin(delta) * Math.cos(theta)
		);
		const lambda2 =
			lambda1 +
			Math.atan2(
				Math.sin(theta) * Math.sin(delta) * Math.cos(phi1),
				Math.cos(delta) - Math.sin(phi1) * Math.sin(phi2)
			);
		return { lat: (phi2 * 180) / Math.PI, lng: (lambda2 * 180) / Math.PI };
	};

	// Update the polyline on the map based on the current latLng and azimuth.
	const updatePolyline = () => {
		if (!map || !latLng || azimuth === undefined) return;
		const end = destPoint(latLng.lat, latLng.lng, azimuth);
		const path = [latLng, end];
		if (direction) {
			direction.setPath(path);
		} else {
			direction = new google.maps.Polyline({
				map,
				path,
				strokeColor: "#fbbc05",
				strokeOpacity: 0.9,
				strokeWeight: 3,
				icons: [
					{
						icon: {
							path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
							scale: 3
						},
						offset: "100%"
					}
				]
			});
		}
	};

	// Set the marker on the map at the given position, updating the latLng state and zooming in if necessary.
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
		updatePolyline();
	};

	// Reactively update the marker position when latLng changes.
	$effect(() => {
		if (latLng && map && window.google) {
			const coords = new google.maps.LatLng(latLng);
			setMarker(coords);
		}
	});

	// Reactively update the polyline when latLng or azimuth changes.
	$effect(() => {
		if (latLng && azimuth) {
			updatePolyline();
		}
	});

	// Initialize the map with a random map ID and set up the click listener to place markers.
	const initMap = async () => {
		const { Map } = (await google.maps.importLibrary("maps")) as google.maps.MapsLibrary;
		const map = new Map(mapDiv, {
			clickableIcons: false,
			center: latLng,
			zoom: 20,
			mapId: crypto.randomUUID(),
			mapTypeId: "satellite",
			tilt: 0
		});
		map.addListener("click", (event: google.maps.MapMouseEvent) => {
			const position = event.latLng!;
			setMarker(position);
		});
		return map;
	};

	// Load the Google Maps API and initialize the map when the component mounts.
	onMount(async () => {
		await googleLoader();
		map = await initMap();
	});
</script>

<div id="google-map" class="h-full w-full" {...props} bind:this={mapDiv}></div>
