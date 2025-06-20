import { text, type RequestHandler } from "@sveltejs/kit";

const GET: RequestHandler = async () => {
	return text("OK");
};

export { GET };
