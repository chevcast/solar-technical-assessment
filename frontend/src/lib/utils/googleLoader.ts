import { env } from "$env/dynamic/public";

const googleLoader = async () => {
	const apiKey = env.PUBLIC_GOOGLE_MAPS_API_KEY;

	return new Promise<void>((resolve, reject) => {
		if (window.google) {
			return resolve();
		}
		const script = document.createElement("script");
		script.async = true;
		const scriptSrc = new URL("https://maps.googleapis.com/maps/api/js");
		scriptSrc.searchParams.append("key", apiKey);
		scriptSrc.searchParams.append("libraries", "places");
		script.src = scriptSrc.toString();
		script.onload = () => resolve();
		script.onerror = (error) => reject(error);
		document.head.appendChild(script);
	});
};

export { googleLoader };
