import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { TranscriptLine } from "@/lib/types";

export function TranscriptRail({
  lines,
  themName,
  youName,
}: {
  lines: TranscriptLine[];
  themName: string;
  youName: string;
}) {
  return (
    <ScrollArea className="h-full">
      <div className="space-y-3 p-1">
        {lines.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Transcript is empty. Play a mock question or turn on the mic — VEIL never joins the call as a bot.
          </p>
        ) : (
          lines.map((line) => (
            <div key={line.id} className="space-y-1">
              <p className="text-[0.65rem] font-medium uppercase tracking-[0.16em] text-muted-foreground">
                {line.speaker === "you" ? youName : line.speaker === "them" ? themName : "Room"}
              </p>
              <p
                className={cn(
                  "text-sm leading-relaxed",
                  line.speaker === "them" ? "text-foreground" : "text-muted-foreground",
                )}
              >
                {line.text}
              </p>
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  );
}
