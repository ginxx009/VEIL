import { useState } from "react";
import { toast } from "sonner";
import { DualView } from "@/components/dual-view";
import { MeetingStage } from "@/components/meeting-stage";
import { OverlayPanel } from "@/components/overlay-panel";
import { LANDING_SAMPLE_ANSWER } from "@/lib/sample-data";
import type { ViewMode } from "@/lib/types";

export function LandingDemo() {
  const [stealthOn, setStealthOn] = useState(true);
  const [overlayVisible, setOverlayVisible] = useState(true);
  const [view, setView] = useState<ViewMode>("split");
  const [prompt, setPrompt] = useState("");

  return (
    <div className="flex min-h-0 flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        {(["split", "you", "them"] as ViewMode[]).map((v) => (
          <button
            key={v}
            type="button"
            onClick={() => setView(v)}
            className={`h-9 rounded-full px-3 text-xs font-medium ${
              view === v ? "bg-secondary text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {v === "split" ? "Split" : v === "you" ? "You" : "Them"}
          </button>
        ))}
      </div>
      <div className="min-h-[22rem] md:min-h-[26rem]">
        <DualView
          view={view}
          stealthOn={stealthOn}
          overlayVisible={overlayVisible}
          you={<MeetingStage mode="interview" youName="Alex Rivera" elapsed={312} />}
          them={<MeetingStage mode="interview" youName="Alex Rivera" elapsed={312} />}
          overlay={
            <OverlayPanel
              stealthOn={stealthOn}
              visible
              status="ready"
              result={LANDING_SAMPLE_ANSWER}
              error={null}
              prompt={prompt}
              onPrompt={setPrompt}
              onAssist={() => toast.message("Open the copilot to generate live answers.")}
              onScreen={() => toast.message("Open the copilot to solve the shared screen.")}
              onToggleStealth={() => setStealthOn((s) => !s)}
              onHide={() => setOverlayVisible(false)}
            />
          }
        />
      </div>
      {!overlayVisible ? (
        <button
          type="button"
          className="self-start text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
          onClick={() => setOverlayVisible(true)}
        >
          Show overlay again
        </button>
      ) : null}
    </div>
  );
}
