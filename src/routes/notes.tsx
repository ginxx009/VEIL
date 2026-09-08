import { useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { VeilWordmark } from "@/components/logo";
import { NotesBody } from "@/components/notes-body";
import { Button } from "@/components/ui/button";
import { MODE_COPY } from "@/lib/sample-data";
import { loadSessions } from "@/lib/storage";
import type { SavedSession } from "@/lib/types";
import { formatClock } from "@/lib/utils";

export const Route = createFileRoute("/notes")({ component: NotesPage });

function NotesPage() {
  const [sessions, setSessions] = useState<SavedSession[]>([]);
  const [openId, setOpenId] = useState("");

  useEffect(() => {
    const all = loadSessions();
    setSessions(all);
    setOpenId((id) => id || all[0]?.id || "");
  }, []);

  const current = sessions.find((s) => s.id === openId) ?? sessions[0];

  return (
    <div className="min-h-dvh bg-background">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-5 py-5">
        <Link to="/">
          <VeilWordmark />
        </Link>
        <Button size="sm" asChild>
          <Link to="/session">New room</Link>
        </Button>
      </header>
      <main className="mx-auto grid max-w-5xl gap-8 px-5 pb-16 lg:grid-cols-[16rem_1fr]">
        <aside>
          <h1 className="font-display text-3xl tracking-tight">Notes</h1>
          <p className="mt-2 text-sm text-muted-foreground">Stored on this device only.</p>
          <ul className="mt-6 space-y-1">
            {sessions.length === 0 ? (
              <li className="text-sm text-muted-foreground">No rooms yet.</li>
            ) : (
              sessions.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    onClick={() => setOpenId(s.id)}
                    className={`w-full rounded-md px-3 py-2 text-left text-sm ${
                      current?.id === s.id ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <span className="block truncate">{s.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {MODE_COPY[s.mode].label} · {formatClock(s.durationSec)}
                    </span>
                  </button>
                </li>
              ))
            )}
          </ul>
        </aside>
        <section>
          {current?.notes ? (
            <>
              <p className="text-xs uppercase tracking-widest text-muted-foreground">{current.title}</p>
              <NotesBody notes={current.notes} />
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Finish a room to generate notes.</p>
          )}
        </section>
      </main>
    </div>
  );
}
