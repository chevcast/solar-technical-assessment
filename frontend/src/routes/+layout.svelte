<script lang="ts">
	import "../app.css";
	import { page } from "$app/state";
	let { children } = $props();
	const {
		seo = {
			title: "Solar Technical Assessment",
			description: "",
			image: "",
			url: ""
		}
	} = page.data;
</script>

<svelte:head>
	<title>{seo.title}</title>

	<!-- Basic meta tags -->
	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<link rel="icon" href="/images/favicon.ico" />

	<!-- Open Graph tags -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content={seo.url} />
	<meta property="og:title" content={seo.title} />
	<meta property="og:description" content={seo.description} />
	<meta property="og:image" content={seo.image} />
	<meta property="og:image:width" content="600" />
	<meta property="og:image:height" content="500" />

	<!-- Twitter Card tags -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="@ChevCast" />
	<meta name="twitter:title" content={seo.title} />
	<meta name="twitter:description" content={seo.description} />
	<meta name="twitter:image" content={seo.image} />

	<!-- Fallback description for non–social contexts -->
	<meta name="description" content={seo.description} />
</svelte:head>

{@render children()}
