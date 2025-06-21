import { defineConfig, loadEnv } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
	// load .env so we can read VITE_API_URL at “vite dev”
	const { API_URL } = loadEnv(mode, process.cwd(), "");

	return {
		plugins: [tailwindcss(), sveltekit()],

		server: {
			host: "0.0.0.0",
			port: 3000,
			strictPort: true,

			/** Built-in Vite proxy → Django */
			proxy: {
				"/api": {
					target: API_URL, // e.g. http://localhost:8000
					changeOrigin: true, // Host header → API host
					secure: false // allow self-signed certs in dev
				}
			}
		},

		preview: {
			host: "0.0.0.0",
			port: 3000,
			strictPort: true
		}
	};
});
