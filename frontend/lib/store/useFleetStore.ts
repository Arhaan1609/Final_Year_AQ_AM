import { create } from "zustand";
import { FleetVehicle, CopilotMessage } from "../api/types";
import { MOCK_VEHICLES, getOrCreateCustomVehicle } from "../api/mock";
import { isMockMode, setMockModeOverride } from "../api/client";

export type DashboardTab =
  | "fleet"
  | "state-est"
  | "thermal"
  | "behavior"
  | "knee"
  | "meta-ensemble";

export type ThemeMode = "light" | "dark";
export type VehicleStatusFilter = "all" | "active" | "warning" | "critical" | "charging";

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
  theme: ThemeMode;
  vehicles: FleetVehicle[];
  selectedVehicleId: string;
  activeTab: DashboardTab;
  isMock: boolean;
  copilotOpen: boolean;
  copilotMessages: CopilotMessage[];
  telemetry: TelemetryInputs;
  isLiveUpdating: boolean;

  // Enterprise Search & Filters
  searchQuery: string;
  statusFilter: VehicleStatusFilter;
  hubFilter: string;

  // Actions
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
  setSelectedVehicle: (id: string) => void;
  setActiveTab: (tab: DashboardTab) => void;
  setIsMock: (mock: boolean) => void;
  setCopilotOpen: (open: boolean) => void;
  addCopilotMessage: (msg: Omit<CopilotMessage, "id" | "timestamp">) => void;
  clearCopilot: () => void;
  updateTelemetry: (inputs: Partial<TelemetryInputs>) => void;
  toggleLiveUpdating: () => void;
  getSelectedVehicle: () => FleetVehicle;

  // Enterprise lookup actions
  setSearchQuery: (q: string) => void;
  setStatusFilter: (s: VehicleStatusFilter) => void;
  setHubFilter: (h: string) => void;
  lookupOrAddVehicle: (id: string) => FleetVehicle;
  getFilteredVehicles: () => FleetVehicle[];
}

const INITIAL_COPILOT_MESSAGES: CopilotMessage[] = [
  {
    id: "welcome-1",
    sender: "assistant",
    text: "👋 **Hello! I am your Enterprise Fleet Copilot.**\n\nI have direct access to your 74 trained models across all 3 modules. You can ask me to evaluate ANY vehicle in the enterprise fleet, lookup thermal hazards, predict knee points, or analyze driver strain.",
    timestamp: "Just now",
  },
];

export const useFleetStore = create<FleetStoreState>((set, get) => ({
  theme: "light",
  vehicles: MOCK_VEHICLES,
  selectedVehicleId: MOCK_VEHICLES[0].id,
  activeTab: "fleet",
  isMock: true,
  copilotOpen: false,
  copilotMessages: INITIAL_COPILOT_MESSAGES,
  isLiveUpdating: true,

  searchQuery: "",
  statusFilter: "all",
  hubFilter: "all",

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

  setTheme: (theme: ThemeMode) => set({ theme }),
  toggleTheme: () => set((state) => ({ theme: state.theme === "light" ? "dark" : "light" })),

  setSelectedVehicle: (id: string) => {
    const cleanId = id.trim();
    let v = get().vehicles.find((item) => item.id.toUpperCase() === cleanId.toUpperCase());
    if (!v) {
      v = get().lookupOrAddVehicle(cleanId);
    }

    if (v) {
      set({
        selectedVehicleId: v.id,
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
    return (
      vehicles.find((v) => v.id.toUpperCase() === selectedVehicleId.toUpperCase()) ||
      vehicles[0]
    );
  },

  setSearchQuery: (q: string) => set({ searchQuery: q }),
  setStatusFilter: (s: VehicleStatusFilter) => set({ statusFilter: s }),
  setHubFilter: (h: string) => set({ hubFilter: h }),

  lookupOrAddVehicle: (id: string) => {
    const vehicle = getOrCreateCustomVehicle(id);
    set((state) => {
      const exists = state.vehicles.some((v) => v.id === vehicle.id);
      return exists ? {} : { vehicles: [vehicle, ...state.vehicles] };
    });
    return vehicle;
  },

  getFilteredVehicles: () => {
    const { vehicles, searchQuery, statusFilter, hubFilter } = get();
    const query = searchQuery.trim().toLowerCase();

    return vehicles.filter((v) => {
      const matchesSearch =
        !query ||
        v.id.toLowerCase().includes(query) ||
        v.driver.toLowerCase().includes(query) ||
        v.model.toLowerCase().includes(query) ||
        v.fleet.toLowerCase().includes(query);

      const matchesStatus =
        statusFilter === "all" || v.status === statusFilter;

      const matchesHub =
        hubFilter === "all" || v.fleet.toLowerCase().includes(hubFilter.toLowerCase());

      return matchesSearch && matchesStatus && matchesHub;
    });
  },
}));
