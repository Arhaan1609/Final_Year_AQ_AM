"use client";

import React, { useState, useRef, useEffect } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { askCopilot } from "../../lib/api/copilot";
import { Badge } from "../ui/Badge";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  X,
  Send,
  Cpu,
  ChevronDown,
  ChevronRight,
  Trash2,
} from "lucide-react";

export const CopilotDrawer: React.FC = () => {
  const { copilotOpen, setCopilotOpen, copilotMessages, addCopilotMessage, clearCopilot } =
    useFleetStore();

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [openTools, setOpenTools] = useState<Record<string, boolean>>({});

  const scrollRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "Is GJ05CV6564 at risk of thermal failure?",
    "Which vehicle is closest to its degradation knee point?",
    "How is Rajesh Sharma driving on battery stress?",
    "Give full digital-twin diagnosis for GJ05AX4321",
  ];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [copilotMessages, loading]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    setInput("");
    addCopilotMessage({ sender: "user", text });

    setLoading(true);
    try {
      const res = await askCopilot(text, copilotMessages);
      addCopilotMessage({
        sender: "assistant",
        text: res.reply,
        toolCalls: res.toolCalls,
      });
    } catch (e) {
      console.error(e);
      addCopilotMessage({
        sender: "assistant",
        text: "I encountered an issue querying the telemetry models. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleTool = (id: string) => {
    setOpenTools((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <AnimatePresence>
      {copilotOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setCopilotOpen(false)}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40"
          />

          {/* Drawer Panel */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 bottom-0 w-full max-w-md bg-white dark:bg-[#0D121F] border-l border-slate-200 dark:border-slate-800 shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between bg-slate-50 dark:bg-slate-950/40">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-cyan-100 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-800 flex items-center justify-center text-cyan-700 dark:text-cyan-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    Fleet AI Copilot
                    <Badge variant="cyan" size="sm">FastMCP Live</Badge>
                  </h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">Natural Language Telemetry Agent</p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={clearCopilot}
                  title="Clear Chat History"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setCopilotOpen(false)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Chat Body */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
              {copilotMessages.map((msg, index) => (
                <div
                  key={msg.id || index}
                  className={`flex flex-col ${
                    msg.sender === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-[88%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-cyan-600 text-white rounded-br-none shadow-sm"
                        : "bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none"
                    }`}
                  >
                    <div className="whitespace-pre-line font-sans">{msg.text}</div>

                    {/* Tool Call Chips for Assistant */}
                    {msg.toolCalls && msg.toolCalls.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-slate-200 dark:border-slate-800 space-y-2">
                        {msg.toolCalls.map((tc, tcIndex) => {
                          const toolId = `${msg.id}-tool-${tcIndex}`;
                          const isOpen = !!openTools[toolId];
                          return (
                            <div
                              key={tcIndex}
                              className="rounded-lg bg-white dark:bg-slate-950/80 border border-cyan-200 dark:border-cyan-500/30 overflow-hidden"
                            >
                              <div
                                onClick={() => toggleTool(toolId)}
                                className="px-2.5 py-1.5 flex items-center justify-between text-[10px] font-mono text-cyan-800 dark:text-cyan-300 cursor-pointer hover:bg-cyan-50 dark:hover:bg-cyan-950/30 transition-colors select-none"
                              >
                                <span className="flex items-center gap-1.5">
                                  <Cpu className="w-3 h-3 text-cyan-600 dark:text-cyan-400" />
                                  Used Live Model: <strong>{tc.tool}()</strong>
                                </span>
                                {isOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                              </div>

                              {isOpen && (
                                <div className="p-2 bg-slate-50 dark:bg-slate-950 text-[10px] font-mono text-slate-600 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800 overflow-x-auto">
                                  <div className="text-cyan-700 dark:text-cyan-400">Args: {JSON.stringify(tc.args)}</div>
                                  <div className="text-emerald-700 dark:text-emerald-400 mt-1">Result: {JSON.stringify(tc.result)}</div>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 font-mono px-1">
                    {msg.timestamp}
                  </span>
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-2 text-xs font-mono text-cyan-600 dark:text-cyan-400 p-2">
                  <Sparkles className="w-3.5 h-3.5 animate-spin" />
                  <span>Agent analyzing live model telemetry...</span>
                </div>
              )}
            </div>

            {/* Suggested Question Chips */}
            <div className="p-3 bg-slate-50 dark:bg-slate-950/60 border-t border-slate-200 dark:border-slate-800/80 space-y-1.5">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Suggested Telemetry Queries:
              </div>
              <div className="flex flex-wrap gap-1.5">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(q)}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:border-cyan-400 transition-all text-left truncate max-w-full shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="p-3 bg-white dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="Ask about thermal risks, knee cycles, driver AI..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500 font-sans"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
