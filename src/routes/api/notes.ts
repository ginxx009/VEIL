import { createFileRoute } from "@tanstack/react-router";
import { runNotes, type NotesInput } from "@/lib/ai";

export const Route = createFileRoute("/api/notes")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const data = (await request.json()) as NotesInput;
        const result = await runNotes(data);
        return Response.json(result);
      },
    },
  },
});
