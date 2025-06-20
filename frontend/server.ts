import { handler } from "./build/handler.js";
import { createServer } from "http";
const server = createServer((req, res) => {
	handler(req, res, () => {
		res.writeHead(404);
		res.end("Not found");
	});
});

server.listen(3000, "0.0.0.0");
