import { defineConfig, loadEnv } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
	const { API_URL } = loadEnv(mode, process.cwd(), "");

	return {
		plugins: [tailwindcss(), sveltekit()],

		server: {
			host: "0.0.0.0",
			port: 3000,
			strictPort: true,

			proxy: {
				"/api": {
					target: API_URL,
					changeOrigin: true,
					secure: false
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
