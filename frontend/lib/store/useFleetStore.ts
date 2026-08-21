import { create } from "zustand";
import { FleetVehicle, CopilotMessage } from "../api/types";
import { MOCK_VEHICLES } from "../api/mock";
import { isMockMode, setMockModeOverride } from "../api/client";

export type DashboardTab =
  | "fleet"
  | "state-est"
  | "thermal"
  | "behavior"
  | "knee"
  | "meta-ensemble";

interface TelemetryInputs {
  voltage: number;
  current: number;
  temperature: number;
  odometer: number;
  cycleCount: number;
  avgSpeed: number;
  maxSpeed: number;
  harshAccel: number;
  harshBrake: number;
  harshCorner: number;
}

interface FleetStoreState {
  vehicles: FleetVehicle[];
  selectedVehicleId: string;
  activeTab: DashboardTab;
  isMock: boolean;
  copilotOpen: boolean;
  copilotMessages: CopilotMessage[];
  telemetry: TelemetryInputs;
  isLiveUpdating: boolean;

  // Actions
  setSelectedVehicle: (id: string) => void;
  setActiveTab: (tab: DashboardTab) => void;
  setIsMock: (mock: boolean) => void;
  setCopilotOpen: (open: boolean) => void;
  addCopilotMessage: (msg: Omit<CopilotMessage, "id" | "timestamp">) => void;
  clearCopilot: () => void;
  updateTelemetry: (inputs: Partial<TelemetryInputs>) => void;
  toggleLiveUpdating: () => void;
  getSelectedVehicle: () => FleetVehicle;
}

const INITIAL_COPILOT_MESSAGES: CopilotMessage[] = [
  {
    id: "welcome-1",
    sender: "assistant",
    text: "👋 **Hello! I am your AI Fleet Copilot.**\n\nI have direct tool-calling access to your 74 trained models across all 3 modules. You can ask me about live vehicle thermal risks, knee-point aging, driver behavior aggression, or full digital-twin health reports.",
    timestamp: "Just now",
  },
];

export const useFleetStore = create<FleetStoreState>((set, get) => ({
  vehicles: MOCK_VEHICLES,
  selectedVehicleId: MOCK_VEHICLES[0].id,
  activeTab: "fleet",
  isMock: true,
  copilotOpen: false,
  copilotMessages: INITIAL_COPILOT_MESSAGES,
  isLiveUpdating: true,

  telemetry: {
    voltage: 75.8,
    current: -18.4,
    temperature: 33.2,
    odometer: 12500,
    cycleCount: 215,
    avgSpeed: 34.2,
    maxSpeed: 62.0,
    harshAccel: 2,
    harshBrake: 1,
    harshCorner: 1,
  },

  setSelectedVehicle: (id: string) => {
    const v = get().vehicles.find((item) => item.id === id);
    if (v) {
      set({
        selectedVehicleId: id,
        telemetry: {
          voltage: v.voltage,
          current: v.current,
          temperature: v.battery_temp,
          odometer: Math.floor(v.charge_cycle_count * 58),
          cycleCount: v.charge_cycle_count,
          avgSpeed: v.speed,
          maxSpeed: v.speed + 25,
          harshAccel: v.status === "warning" ? 5 : v.status === "critical" ? 8 : 2,
          harshBrake: v.status === "critical" ? 6 : 2,
          harshCorner: 2,
        },
      });
    }
  },

  setActiveTab: (tab: DashboardTab) => set({ activeTab: tab }),

  setIsMock: (mock: boolean) => {
    setMockModeOverride(mock);
    set({ isMock: mock });
  },

  setCopilotOpen: (open: boolean) => set({ copilotOpen: open }),

  addCopilotMessage: (msg) => {
    const newMsg: CopilotMessage = {
      ...msg,
      id: "msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    set((state) => ({
      copilotMessages: [...state.copilotMessages, newMsg],
    }));
  },

  clearCopilot: () => set({ copilotMessages: INITIAL_COPILOT_MESSAGES }),

  updateTelemetry: (inputs) =>
    set((state) => ({
      telemetry: { ...state.telemetry, ...inputs },
    })),

  toggleLiveUpdating: () =>
    set((state) => ({ isLiveUpdating: !state.isLiveUpdating })),

  getSelectedVehicle: () => {
    const { vehicles, selectedVehicleId } = get();
    return vehicles.find((v) => v.id === selectedVehicleId) || vehicles[0];
  },
}));
