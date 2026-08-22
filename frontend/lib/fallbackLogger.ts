import { create } from "zustand";

export interface FallbackEvent {
  id: string;
  timestamp: string;
  component: string;
  field: string;
  receivedValue: string;
  defaultedTo: string;
  severity: "low" | "medium" | "high";
  reason: string;
}

interface FallbackState {
  events: FallbackEvent[];
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  addEvent: (evt: Omit<FallbackEvent, "id" | "timestamp">) => void;
  clearEvents: () => void;
}

export const useFallbackStore = create<FallbackState>((set) => ({
  events: [],
  isOpen: false,
  setIsOpen: (isOpen) => set({ isOpen }),
  addEvent: (evt) => {
    const newEvent: FallbackEvent = {
      ...evt,
      id: "fb-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4),
      timestamp: new Date().toLocaleTimeString(),
    };
    console.warn(
      `[DATA FALLBACK WARNING] Component: ${evt.component} | Field: ${evt.field} | Received: ${evt.receivedValue} | Defaulted To: ${evt.defaultedTo} | Reason: ${evt.reason}`
    );
    set((state) => ({ events: [newEvent, ...state.events.slice(0, 49)] }));
  },
  clearEvents: () => set({ events: [] }),
}));

export function reportFallback(
  component: string,
  field: string,
  receivedValue: any,
  defaultedTo: any,
  reason: string,
  severity: "low" | "medium" | "high" = "medium"
) {
  useFallbackStore.getState().addEvent({
    component,
    field,
    receivedValue: receivedValue === undefined ? "undefined" : receivedValue === null ? "null" : String(receivedValue),
    defaultedTo: String(defaultedTo),
    severity,
    reason,
  });
}
