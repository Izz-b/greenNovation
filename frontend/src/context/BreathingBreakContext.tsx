import { createContext, useContext, type ReactNode } from "react";

type BreathingBreakContextValue = {
  openBreathingBreak: () => void;
};

const BreathingBreakContext = createContext<BreathingBreakContextValue | null>(null);

export function BreathingBreakProvider({
  children,
  openBreathingBreak,
}: {
  children: ReactNode;
  openBreathingBreak: () => void;
}) {
  return (
    <BreathingBreakContext.Provider value={{ openBreathingBreak }}>{children}</BreathingBreakContext.Provider>
  );
}

export function useBreathingBreakOptional() {
  return useContext(BreathingBreakContext);
}

export function useOpenBreathingBreak() {
  const ctx = useContext(BreathingBreakContext);
  return ctx?.openBreathingBreak ?? null;
}
