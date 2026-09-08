import type { SessionNotes } from "@/lib/types";

export function NotesBody({ notes }: { notes: SessionNotes }) {
  return (
    <div className="mt-8 space-y-8">
      <section>
        <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">Summary</h2>
        <p className="mt-2 text-sm leading-relaxed text-foreground">{notes.summary}</p>
      </section>
      {notes.keyPoints.length ? <List title="Key points" items={notes.keyPoints} /> : null}
      {notes.questions.length ? <List title="Questions asked" items={notes.questions} /> : null}
      {notes.actionItems.length ? <List title="Action items" items={notes.actionItems} /> : null}
      {notes.followUpEmail ? (
        <section>
          <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">Follow-up</h2>
          <pre className="mt-2 whitespace-pre-wrap rounded-xl bg-card p-4 text-sm leading-relaxed text-foreground shadow-[var(--shadow-border)]">
            {notes.followUpEmail}
          </pre>
        </section>
      ) : null}
    </div>
  );
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <section>
      <h2 className="text-xs font-medium uppercase tracking-widest text-muted-foreground">{title}</h2>
      <ul className="mt-2 space-y-2">
        {items.map((item) => (
          <li key={item} className="flex gap-2 text-sm text-foreground">
            <span className="mt-2 size-1 shrink-0 rounded-full bg-sage" />
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}
