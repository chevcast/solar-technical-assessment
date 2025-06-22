import { text, type RequestHandler } from "@sveltejs/kit";

// Respond to health check requests with a simple "OK" message
const GET: RequestHandler = async () => {
	return text("OK");
};

export { GET };
