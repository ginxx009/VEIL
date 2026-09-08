import { createFileRoute } from "@tanstack/react-router";
import { runAssist, type AssistInput } from "@/lib/ai";

export const Route = createFileRoute("/api/assist")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const data = (await request.json()) as AssistInput;
        const result = await runAssist(data);
        return Response.json(result);
      },
    },
  },
});
