import { useCallback, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import {
  Eye,
  EyeOff,
  LayoutGrid,
  Mic,
  MicOff,
  Monitor,
  PanelLeft,
  PhoneOff,
  Play,
} from "lucide-react";
import { toast } from "sonner";
import { DualView } from "@/components/dual-view";
import { VeilWordmark } from "@/components/logo";
import { MeetingStage, screenContentText } from "@/components/meeting-stage";
import { NotesBody } from "@/components/notes-body";
import { OverlayPanel } from "@/components/overlay-panel";
import { TranscriptRail } from "@/components/transcript-rail";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { generateAssist, generateNotes } from "@/lib/ai";
import { MODE_COPY, MOCK_QUESTIONS } from "@/lib/sample-data";
import { loadProfile, saveProfile, upsertSession } from "@/lib/storage";
import type {
  AssistResult,
  AssistStatus,
  MeetingMode,
  Profile,
  SessionNotes,
  SessionPhase,
  TranscriptLine,
  ViewMode,
} from "@/lib/types";
import { cn, sleep } from "@/lib/utils";

export const Route = createFileRoute("/session")({ component: SessionPage });

const MAX_ASSISTS = 12;

type Rec = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((ev: { resultIndex: number; results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
};

function SessionPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<Profile>(loadProfile);
  const [phase, setPhase] = useState<SessionPhase>("setup");
  const [stealthOn, setStealthOn] = useState(true);
  const [overlayVisible, setOverlayVisible] = useState(true);
  const [view, setView] = useState<ViewMode>("split");
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState<AssistStatus>("idle");
  const [result, setResult] = useState<AssistResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [listening, setListening] = useState(false);
  const [mockIndex, setMockIndex] = useState(0);
  const [assistCount, setAssistCount] = useState(0);
  const [notes, setNotes] = useState<SessionNotes | null>(null);
  const [notesBusy, setNotesBusy] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [railOpen, setRailOpen] = useState(true);
  const recognitionRef = useRef<Rec | null>(null);
  const startedAtRef = useRef(0);

  useEffect(() => {
    setProfile(loadProfile());
  }, []);

  useEffect(() => {
    if (phase !== "live") return;
    const t = window.setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => window.clearInterval(t);
  }, [phase]);

  const addLine = useCallback((speaker: TranscriptLine["speaker"], text: string) => {
    const line: TranscriptLine = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      speaker,
      text,
      at: Date.now(),
    };
    setTranscript((prev) => [...prev, line]);
    return line;
  }, []);

  const runAssist = useCallback(
    async (kind: "answer" | "screen", questionOverride?: string, extraTranscript?: string) => {
      if (status === "thinking") return;
      if (assistCount >= MAX_ASSISTS) {
        toast.error("Assist limit reached for this room");
        return;
      }
      const question = (questionOverride ?? prompt).trim();
      setStatus("thinking");
      setError(null);
      setOverlayVisible(true);
      const packed = [
        ...transcript.map((l) => `${l.speaker}: ${l.text}`),
        extraTranscript,
      ]
        .filter(Boolean)
        .join("\n");
      try {
        const res = await generateAssist({
          data: {
            mode: profile.mode,
            kind,
            resume: profile.resume,
            job: profile.jobDescription,
            transcript: packed,
            question,
            screenText: screenContentText(profile.mode),
          },
        });
        if (!res.ok) {
          setStatus("error");
          setError(res.error);
          return;
        }
        setAssistCount((c) => c + 1);
        setStatus("ready");
        const words = res.result.spoken.split(" ");
        let acc = "";
        for (const w of words) {
          acc += (acc ? " " : "") + w;
          setResult({ spoken: acc, points: [], code: "" });
          await sleep(18);
        }
        setResult(res.result);
        setPrompt("");
      } catch {
        setStatus("error");
        setError("Could not reach the model.");
      }
    },
    [assistCount, profile, prompt, status, transcript],
  );

  const playMock = useCallback(async () => {
    const list = MOCK_QUESTIONS[profile.mode];
    const q = list[mockIndex % list.length];
    setMockIndex((i) => i + 1);
    addLine("them", q);
    await sleep(200);
    await runAssist("answer", q, `them: ${q}`);
  }, [addLine, mockIndex, profile.mode, runAssist]);

  const toggleMic = useCallback(() => {
    const win = window as unknown as { SpeechRecognition?: new () => Rec; webkitSpeechRecognition?: new () => Rec };
    const SR = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SR) {
      toast.error("This browser has no speech recognition. Use mock questions.");
      return;
    }
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = false;
    rec.lang = "en-US";
    rec.onresult = (ev) => {
      const text = Array.from(ev.results)
        .slice(ev.resultIndex)
        .map((r) => r[0]?.transcript ?? "")
        .join(" ")
        .trim();
      if (text) addLine("room", text);
    };
    rec.onerror = () => {
      setListening(false);
      toast.error("Microphone unavailable. Use mock questions.");
    };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    try {
      rec.start();
      setListening(true);
    } catch {
      toast.error("Could not start the microphone.");
    }
  }, [addLine, listening]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (phase !== "live") return;
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "Enter") {
        e.preventDefault();
        void runAssist("answer");
      }
      if (mod && e.shiftKey && e.key.toLowerCase() === "e") {
        e.preventDefault();
        setStealthOn((s) => !s);
      }
      if (mod && e.shiftKey && e.key.toLowerCase() === "h") {
        e.preventDefault();
        setOverlayVisible((v) => !v);
      }
      if (mod && e.shiftKey && e.key.toLowerCase() === "s") {
        e.preventDefault();
        void runAssist("screen");
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, runAssist]);

  useEffect(() => {
    return () => recognitionRef.current?.stop();
  }, []);

  const enterRoom = () => {
    saveProfile(profile);
    setSessionId(`veil-${Date.now()}`);
    startedAtRef.current = Date.now();
    setElapsed(0);
    setTranscript([]);
    setResult(null);
    setStatus("idle");
    setAssistCount(0);
    setMockIndex(0);
    setNotes(null);
    setStealthOn(true);
    setOverlayVisible(true);
    setPhase("live");
    if (window.matchMedia("(max-width: 1023px)").matches) {
      setView("you");
      setRailOpen(false);
    }
  };

  const endRoom = async () => {
    recognitionRef.current?.stop();
    setListening(false);
    setNotesBusy(true);
    setPhase("notes");
    const packed = transcript.map((l) => `${l.speaker}: ${l.text}`).join("\n");
    let nextNotes: SessionNotes | null = null;
    if (packed.trim()) {
      const res = await generateNotes({
        data: {
          mode: profile.mode,
          resume: profile.resume,
          job: profile.jobDescription,
          transcript: packed,
        },
      });
      if (res.ok) nextNotes = res.notes;
      else toast.error(res.error);
    } else {
      nextNotes = {
        summary: "No transcript was captured.",
        keyPoints: [],
        questions: [],
        actionItems: [],
        followUpEmail: "",
      };
    }
    setNotes(nextNotes);
    setNotesBusy(false);
    upsertSession({
      id: sessionId || `veil-${Date.now()}`,
      title: MODE_COPY[profile.mode].meeting,
      mode: profile.mode,
      startedAt: startedAtRef.current || Date.now(),
      durationSec: elapsed,
      transcript,
      notes: nextNotes,
    });
  };

  const copy = MODE_COPY[profile.mode];
  const overlay = (
    <OverlayPanel
      stealthOn={stealthOn}
      visible={overlayVisible}
      status={status}
      result={result}
      error={error}
      prompt={prompt}
      onPrompt={setPrompt}
      onAssist={() => void runAssist("answer")}
      onScreen={() => void runAssist("screen")}
      onToggleStealth={() => setStealthOn((s) => !s)}
      onHide={() => setOverlayVisible(false)}
    />
  );

  if (phase === "setup") {
    return (
      <div className="min-h-dvh bg-background">
        <header className="mx-auto flex max-w-3xl items-center justify-between px-5 py-5">
          <Link to="/">
            <VeilWordmark />
          </Link>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/notes">Past notes</Link>
          </Button>
        </header>
        <main className="mx-auto max-w-3xl px-5 pb-16">
          <h1 className="font-display text-4xl tracking-tight">Enter a room</h1>
          <p className="mt-2 max-w-lg text-sm text-muted-foreground">
            Context stays on this device. Grok only sees what you send for the next answer.
          </p>

          <div className="mt-8 grid gap-2 sm:grid-cols-3">
            {(["interview", "sales", "meeting"] as MeetingMode[]).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setProfile((p) => ({ ...p, mode: m }))}
                className={cn(
                  "rounded-xl p-4 text-left shadow-[var(--shadow-border)] transition-[box-shadow,background-color] duration-150",
                  profile.mode === m ? "bg-secondary" : "bg-card hover:shadow-[var(--shadow-border-hover)]",
                )}
              >
                <p className="font-medium">{MODE_COPY[m].label}</p>
                <p className="mt-1 text-xs text-muted-foreground">{MODE_COPY[m].hint}</p>
              </button>
            ))}
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <Field label="Your name">
              <Input
                value={profile.displayName}
                onChange={(e) => setProfile((p) => ({ ...p, displayName: e.target.value }))}
              />
            </Field>
            <Field label="Role">
              <Input
                value={profile.role}
                onChange={(e) => setProfile((p) => ({ ...p, role: e.target.value }))}
              />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Resume / playbook">
              <Textarea
                value={profile.resume}
                onChange={(e) => setProfile((p) => ({ ...p, resume: e.target.value }))}
                className="min-h-36"
              />
            </Field>
          </div>
          <div className="mt-4">
            <Field label="Job or meeting context">
              <Textarea
                value={profile.jobDescription}
                onChange={(e) => setProfile((p) => ({ ...p, jobDescription: e.target.value }))}
              />
            </Field>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Button size="lg" onClick={enterRoom}>
              Enter {copy.label.toLowerCase()}
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/">Back</Link>
            </Button>
          </div>
        </main>
      </div>
    );
  }

  if (phase === "notes") {
    return (
      <div className="min-h-dvh bg-background">
        <header className="mx-auto flex max-w-3xl items-center justify-between px-5 py-5">
          <Link to="/">
            <VeilWordmark />
          </Link>
          <Button size="sm" variant="outline" onClick={() => setPhase("setup")}>
            New room
          </Button>
        </header>
        <main className="mx-auto max-w-3xl px-5 pb-16">
          <p className="text-xs uppercase tracking-widest text-muted-foreground">{copy.meeting}</p>
          <h1 className="mt-2 font-display text-4xl tracking-tight">Notes</h1>
          {notesBusy ? (
            <p className="veil-shimmer mt-8 bg-clip-text text-muted-foreground">Writing the recap…</p>
          ) : notes ? (
            <NotesBody notes={notes} />
          ) : (
            <p className="mt-8 text-sm text-muted-foreground">No notes for this room.</p>
          )}
          <div className="mt-10 flex gap-3">
            <Button onClick={() => navigate({ to: "/notes" })}>All notes</Button>
            <Button variant="outline" onClick={() => setPhase("setup")}>
              Another room
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex h-dvh flex-col bg-background">
      <header className="flex shrink-0 items-center gap-2 border-b border-border px-3 py-2 md:px-4">
        <Link to="/" className="hidden sm:block">
          <VeilWordmark />
        </Link>
        <span className="truncate text-xs text-muted-foreground sm:ml-3">{copy.meeting}</span>
        <div className="ml-auto flex items-center gap-1">
          {(["split", "you", "them"] as ViewMode[]).map((v) => (
            <button
              key={v}
              type="button"
              onClick={() => setView(v)}
              className={cn(
                "hidden h-9 rounded-full px-3 text-xs font-medium md:inline",
                view === v ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground",
              )}
            >
              {v === "split" ? "Split" : v === "you" ? "You" : "Them"}
            </button>
          ))}
          <Button
            variant={stealthOn ? "sage" : "outline"}
            size="sm"
            onClick={() => setStealthOn((s) => !s)}
            className="rounded-full"
          >
            {stealthOn ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
            <span className="hidden sm:inline">{stealthOn ? "Stealth" : "Visible"}</span>
          </Button>
          <Button variant="destructive" size="sm" className="rounded-full" onClick={() => void endRoom()}>
            <PhoneOff className="size-3.5" />
            End
          </Button>
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="flex min-w-0 flex-1 flex-col p-3 md:p-4">
          <DualView
            view={view}
            stealthOn={stealthOn}
            overlayVisible={overlayVisible}
            you={<MeetingStage mode={profile.mode} youName={profile.displayName} elapsed={elapsed} />}
            them={<MeetingStage mode={profile.mode} youName={profile.displayName} elapsed={elapsed} />}
            overlay={overlay}
          />
          {!overlayVisible ? (
            <button
              type="button"
              className="mt-2 self-start text-xs text-muted-foreground hover:text-foreground"
              onClick={() => setOverlayVisible(true)}
            >
              Show overlay
            </button>
          ) : null}

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Button size="sm" onClick={() => void playMock()}>
              <Play className="size-3.5" />
              Next question
            </Button>
            <Button size="sm" variant={listening ? "sage" : "outline"} onClick={toggleMic}>
              {listening ? <Mic className="size-3.5" /> : <MicOff className="size-3.5" />}
              {listening ? "Listening" : "Mic"}
            </Button>
            <Button size="sm" variant="outline" onClick={() => void runAssist("screen")}>
              <Monitor className="size-3.5" />
              Solve screen
            </Button>
            <Button
              size="icon-sm"
              variant="ghost"
              className="ml-auto md:hidden"
              onClick={() => setView((v) => (v === "you" ? "them" : "you"))}
              aria-label="Swap view"
            >
              <LayoutGrid className="size-4" />
            </Button>
            <Button
              size="icon-sm"
              variant="ghost"
              className="lg:hidden"
              onClick={() => setRailOpen((o) => !o)}
              aria-label="Transcript"
            >
              <PanelLeft className="size-4" />
            </Button>
          </div>
        </div>

        <aside
          className={cn(
            "w-72 shrink-0 flex-col border-l border-border p-4",
            railOpen ? "flex" : "hidden lg:flex",
          )}
        >
          <p className="mb-3 text-xs font-medium uppercase tracking-widest text-muted-foreground">Transcript</p>
          <div className="min-h-0 flex-1">
            <TranscriptRail
              lines={transcript}
              themName={copy.interviewer}
              youName={profile.displayName}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block space-y-2">
      <Label>{label}</Label>
      {children}
    </label>
  );
}
