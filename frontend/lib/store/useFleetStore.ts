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
export type ViewMode = "operations" | "engineering";
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
  viewMode: ViewMode;
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
  setViewMode: (mode: ViewMode) => void;
  toggleViewMode: () => void;
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
    text: "👋 **Hello! I am your Enterprise Fleet Copilot.**\n\nI have direct access to your 74 trained models across all 3 modules and the SQL database. You can ask me to evaluate ANY vehicle in the enterprise fleet, lookup thermal hazards, predict knee points, or analyze driver strain.",
    timestamp: "Just now",
  },
];

export const useFleetStore = create<FleetStoreState>((set, get) => ({
  theme: "light",
  viewMode: "operations", // Default is user-friendly Operations Mode!
  vehicles: MOCK_VEHICLES,
  selectedVehicleId: MOCK_VEHICLES[0]?.id || "DL1LAN0707",
  activeTab: "fleet",
  isMock: false, // LIVE API Connected to port 8000
  copilotOpen: false,
  copilotMessages: INITIAL_COPILOT_MESSAGES,
  isLiveUpdating: true,

  searchQuery: "",
  statusFilter: "all",
  hubFilter: "all",

  telemetry: {
    voltage: MOCK_VEHICLES[0]?.voltage || 73.6,
    current: MOCK_VEHICLES[0]?.current || -14.0,
    temperature: MOCK_VEHICLES[0]?.battery_temp || 29.0,
    odometer: Math.floor((MOCK_VEHICLES[0]?.charge_cycle_count || 80) * 58),
    cycleCount: MOCK_VEHICLES[0]?.charge_cycle_count || 80,
    avgSpeed: MOCK_VEHICLES[0]?.speed || 30.0,
    maxSpeed: (MOCK_VEHICLES[0]?.speed || 30.0) + 25,
    harshAccel: 1,
    harshBrake: 1,
    harshCorner: 1,
  },

  setTheme: (theme: ThemeMode) => set({ theme }),
  toggleTheme: () => set((state) => ({ theme: state.theme === "light" ? "dark" : "light" })),

  setViewMode: (viewMode: ViewMode) => set({ viewMode }),
  toggleViewMode: () =>
    set((state) => ({
      viewMode: state.viewMode === "operations" ? "engineering" : "operations",
    })),

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
          harshAccel: v.status === "warning" ? 5 : v.status === "critical" ? 8 : 1,
          harshBrake: v.status === "critical" ? 6 : 1,
          harshCorner: 1,
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
    return vehicles.filter((v) => {
      // 1. Search Query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matches =
          v.id.toLowerCase().includes(q) ||
          v.driver.toLowerCase().includes(q) ||
          v.fleet.toLowerCase().includes(q) ||
          v.model.toLowerCase().includes(q);
        if (!matches) return false;
      }

      // 2. Status Filter
      if (statusFilter !== "all" && v.status !== statusFilter) {
        return false;
      }

      // 3. Hub Filter
      if (hubFilter !== "all" && !v.fleet.toLowerCase().includes(hubFilter.toLowerCase())) {
        return false;
      }

      return true;
    });
  },
}));
