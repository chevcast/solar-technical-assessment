import { handler } from "./build/handler.js"; // SvelteKit output
import httpProxy from "http-proxy";
import { createServer } from "http";
import "dotenv/config"; // loads API_URL

const API_URL = process.env.API_URL!;
if (!API_URL) {
	throw new Error("Missing API_URL in environment");
}

const proxy = httpProxy.createProxyServer({
	target: API_URL,
	changeOrigin: true,
	secure: false
});
proxy.on("error", (err) => console.error("Proxy error:", err));

const server = createServer((req, res) => {
	if (req.url?.startsWith("/api")) {
		// Hand the request to Django and return immediately
		proxy.web(req, res);
		return;
	}

	// Everything else pass to SvelteKit
	handler(req, res, () => {
		res.writeHead(404, { "Content-Type": "text/plain" });
		res.end("Not found");
	});
});

server.listen(3000, "0.0.0.0", () => console.log(`Prod server running on http://0.0.0.0:3000`));
