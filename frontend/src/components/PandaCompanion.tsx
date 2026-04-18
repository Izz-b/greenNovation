import { Sparkles } from "lucide-react";
import pandaWaving from "@/assets/panda-waving.png";
import pandaReading from "@/assets/panda-reading.png";
import pandaCrying from "@/assets/panda-crying.png";
import pandaAngry from "@/assets/panda-angry.png";

export type PandaMood = "waving" | "reading" | "crying" | "angry";

const PANDA_MAP: Record<PandaMood, string> = {
  waving: pandaWaving,
  reading: pandaReading,
  crying: pandaCrying,
  angry: pandaAngry,
};

const MOOD_ANIMATION: Record<PandaMood, string> = {
  waving: "animate-[panda-wave_2.4s_ease-in-out_infinite]",
  reading: "animate-[panda-read_4s_ease-in-out_infinite]",
  crying: "animate-[panda-cry_2.6s_ease-in-out_infinite]",
  angry: "animate-[panda-angry_0.6s_ease-in-out_infinite]",
};

export function Panda({
  mood = "waving",
  size = 72,
  className = "",
}: {
  mood?: PandaMood;
  size?: number;
  className?: string;
}) {
  return (
    <img
      src={PANDA_MAP[mood]}
      alt={`Bamboo the panda, ${mood}`}
      width={size}
      height={size}
      style={{ width: size, height: size }}
      className={`drop-shadow-md ${MOOD_ANIMATION[mood]} ${className}`}
      loading="lazy"
    />
  );
}

export function AvatarTip({
  message,
  label = "Bamboo",
  mood = "waving",
}: {
  message: string;
  label?: string;
  mood?: PandaMood;
}) {
  return (
    <div className="relative rounded-3xl gradient-forest p-5 overflow-hidden border border-primary/10">
      <div className="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-primary-glow/30 blur-3xl" />
      <div className="absolute bottom-0 left-0 h-24 w-24 rounded-full bg-accent/30 blur-2xl" />
      <div className="relative flex items-start gap-4">
        <Panda mood={mood} size={72} className="shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-primary mb-1">
            <Sparkles className="h-3.5 w-3.5" />
            {label} suggests
          </div>
          <p className="text-sm font-medium text-foreground leading-relaxed">{message}</p>
        </div>
      </div>
    </div>
  );
}
