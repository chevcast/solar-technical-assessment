import tailwindcss from "@tailwindcss/vite";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import basicSsl from "@vitejs/plugin-basic-ssl";

export default defineConfig({
	plugins: [
		basicSsl({
			name: "solar-technical-assessment",
			domains: ["*"]
		}),
		tailwindcss(),
		sveltekit()
	],
	preview: {
		host: "0.0.0.0",
		port: 3000,
		strictPort: true
	},
	server: {
		host: "0.0.0.0",
		allowedHosts: true,
		port: 3000,
		strictPort: true
	}
});
