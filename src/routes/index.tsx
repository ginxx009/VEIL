import type { ReactNode } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { ArrowDown, Command, EyeOff, Menu, Monitor } from "lucide-react";
import { LandingDemo } from "@/components/landing-demo";
import { VeilWordmark } from "@/components/logo";
import { Button } from "@/components/ui/button";
import { LANDING_SAMPLE_ANSWER } from "@/lib/sample-data";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <div className="min-h-dvh bg-background text-foreground">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <VeilWordmark />
        <Button size="sm" asChild>
          <a href="/veil-mac.zip" download>
            Download for Mac
            <ArrowDown className="size-3.5" />
          </a>
        </Button>
      </header>

      <main className="mx-auto max-w-6xl px-5 pb-20">
        <section className="stagger-in grid min-w-0 items-start gap-10 py-6 md:grid-cols-2 md:py-10">
          <div>
            <p className="text-xs font-medium uppercase tracking-widest text-sage">macOS overlay</p>
            <h1 className="mt-3 font-display text-4xl leading-[1.05] tracking-tight text-foreground md:text-6xl">
              A Mac app.
              <br />
              Invisible on their share.
            </h1>
            <p className="mt-4 max-w-xl text-sm text-muted-foreground md:text-base">
              VEIL is a menu-bar overlay — not a browser tab. The window is marked excluded from
              capture, so Zoom, Meet, and Teams never composite it. No bot joins the call.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button size="lg" asChild>
                <a href="/veil-mac.zip" download>
                  Download for Mac
                  <ArrowDown className="size-4" />
                </a>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="#rehearsal">See what they capture</a>
              </Button>
            </div>
            <ol className="mt-8 max-w-xl space-y-3 text-sm text-muted-foreground">
              <li className="flex gap-3">
                <span className="font-mono text-xs text-sage">1</span>
                Download and unzip VEIL on your Mac.
              </li>
              <li className="flex gap-3">
                <span className="font-mono text-xs text-sage">2</span>
                Double-click Launch.command. It creates a local Python environment (Homebrew
                Python will not let pip install system-wide) and VEIL appears in the menu bar.
              </li>
              <li className="flex gap-3">
                <span className="font-mono text-xs text-sage">3</span>
                Add your xAI key in Settings. Share Meet, Zoom, or your editor — never the overlay.
              </li>
            </ol>
          </div>
          <MacHud />
        </section>

        <section className="mt-6 grid gap-3 md:grid-cols-3">
          <Fact
            icon={<EyeOff className="size-4" />}
            title="Excluded from capture"
            body="The overlay sets the macOS window sharing type to none, plus content protection. Their screen share compositor never sees it."
          />
          <Fact
            icon={<Menu className="size-4" />}
            title="Menu bar, no dock"
            body="Runs as a menu-bar extra. No dock icon, no app switcher entry, no address bar. Hide and summon from the extra."
          />
          <Fact
            icon={<Command className="size-4" />}
            title="Hotkeys on the Mac"
            body="⌘↩ assist · ⌘⇧E stealth · ⌘⇧H hide. Mock questions work without a mic. Notes write when you end the room."
          />
        </section>

        <section id="rehearsal" className="mt-16 scroll-mt-8">
          <p className="text-xs font-medium uppercase tracking-widest text-sage">What they capture</p>
          <h2 className="mt-2 font-display text-3xl tracking-tight">You vs their share</h2>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">
            Toggle the views. Split is both. You is the HUD on your display. Them is the meeting
            frame they receive — overlay gone when stealth is on.
          </p>
          <div className="mt-6">
            <LandingDemo />
          </div>
        </section>

        <p className="mt-14 max-w-2xl text-xs leading-relaxed text-muted-foreground">
          Add an xAI API key in VEIL → Settings on first launch, or point it at this app’s assist
          API. The preview you are looking at is the product page; the overlay itself is the Mac
          download.
        </p>
      </main>
    </div>
  );
}

function MacHud() {
  const a = LANDING_SAMPLE_ANSWER;
  return (
    <div className="relative mx-auto w-full min-w-0 max-w-md">
      <div className="overflow-hidden rounded-xl bg-card shadow-[var(--shadow-float),var(--shadow-border)]">
        <div className="flex h-11 items-center gap-2 border-b border-border px-3">
          <span className="flex gap-1.5" aria-hidden>
            <span className="size-2.5 rounded-full bg-destructive/70" />
            <span className="size-2.5 rounded-full bg-warn/80" />
            <span className="size-2.5 rounded-full bg-sage/80" />
          </span>
          <span className="text-xs text-muted-foreground">Staff Engineer · first round</span>
          <span className="ml-auto rounded-full bg-sage-dim px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-sage">
            Stealth on
          </span>
        </div>
        <div className="space-y-2 p-3">
          <div className="flex gap-1">
            <span className="rounded-full bg-secondary px-3 py-1 text-xs">Assist</span>
            <span className="rounded-full bg-secondary px-3 py-1 text-xs text-muted-foreground">Screen</span>
            <span className="rounded-full bg-secondary px-3 py-1 text-xs text-muted-foreground">Next Q</span>
          </div>
          <div className="flex h-10 items-center rounded-lg bg-secondary px-3 text-xs text-muted-foreground">
            Ask, or ⌘↩
          </div>
          <div className="rounded-xl bg-secondary p-3.5">
            <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">Answer</p>
            <p className="mt-2 text-sm leading-relaxed">{a.spoken}</p>
            <ul className="mt-3 space-y-1">
              {a.points.map((p) => (
                <li key={p} className="flex gap-2 text-xs text-muted-foreground">
                  <span className="mt-1 size-1 shrink-0 rounded-full bg-sage" />
                  {p}
                </li>
              ))}
            </ul>
            <pre className="mt-3 overflow-x-auto whitespace-pre-wrap break-all rounded-md bg-background p-2.5 font-mono text-[11px] leading-relaxed text-sage">
              {a.code}
            </pre>
          </div>
        </div>
      </div>
      <p className="mt-3 flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <Monitor className="size-3.5" />
        Menu bar extra · excluded from capture
      </p>
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
