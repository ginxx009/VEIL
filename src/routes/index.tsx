import type { ReactNode } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, EyeOff, Mic, StickyNote } from "lucide-react";
import { LandingDemo } from "@/components/landing-demo";
import { VeilWordmark } from "@/components/logo";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <div className="min-h-dvh bg-background text-foreground">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <VeilWordmark />
        <nav className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/notes">Notes</Link>
          </Button>
          <Button size="sm" asChild>
            <Link to="/session">
              Open copilot
              <ArrowRight className="size-3.5" />
            </Link>
          </Button>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-5 pb-20">
        <section className="stagger-in max-w-3xl py-6 md:py-8">
          <p className="text-xs font-medium uppercase tracking-widest text-sage">Private meeting copilot</p>
          <h1 className="mt-3 font-display text-4xl leading-[1.05] tracking-tight text-foreground md:text-6xl">
            They get the call.
            <br />
            You keep the overlay.
          </h1>
          <p className="mt-4 max-w-xl text-sm text-muted-foreground md:text-base">
            VEIL listens, drafts speakable answers, and sits on your display. Stealth excludes it from
            the shared frame — toggle their screen share below and watch it vanish.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button size="lg" asChild>
              <Link to="/session">
                Enter a room
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <a href="#rehearsal">Rehearse a share</a>
            </Button>
          </div>
        </section>

        <section id="rehearsal" className="scroll-mt-8">
          <LandingDemo />
        </section>

        <section className="mt-16 grid gap-3 md:grid-cols-3">
          <Fact
            icon={<EyeOff className="size-4" />}
            title="Excluded from capture"
            body="The overlay lives on a separate layer. Their screen share compositor never composites it — same idea as a native capture-exclusion flag, rehearsed here in split view."
          />
          <Fact
            icon={<Mic className="size-4" />}
            title="No bot in the call"
            body="Nothing joins Zoom, Meet, or Teams. Mock questions work without a mic. Live assist uses your microphone locally, then Grok writes the answer."
          />
          <Fact
            icon={<StickyNote className="size-4" />}
            title="Notes after, not during"
            body="When the room ends, VEIL turns the transcript into a recap, action items, and a follow-up email you can send."
          />
        </section>

        <p className="mt-14 max-w-2xl text-xs leading-relaxed text-muted-foreground">
          A browser cannot set OS-level capture exclusion (the API desktop apps use). Share a single
          meeting tab and keep VEIL in this window — or pop the overlay out — and it stays off the
          capture. Full-screen share of this tab will include whatever is painted here; use the
          split rehearsal to confirm stealth is on before you present.
        </p>
      </main>
    </div>
  );
}

function Fact({ icon, title, body }: { icon: ReactNode; title: string; body: string }) {
  return (
    <article className="rounded-xl bg-card p-5 shadow-[var(--shadow-border)]">
      <div className="flex size-9 items-center justify-center rounded-md bg-secondary text-sage">{icon}</div>
      <h2 className="mt-4 font-medium text-foreground">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
    </article>
  );
}
