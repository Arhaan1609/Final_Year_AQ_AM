"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Ensure GSAP plugins are registered safely on client side
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export interface ScrollImageSequenceProps {
  /** Folder path under /public (e.g., "/sequence") */
  frameFolder: string;
  /** Total number of frames in the sequence (e.g., 300) */
  frameCount: number;
  /** File prefix before number (e.g., "ezgif-frame-") */
  fileNamePrefix?: string;
  /** File extension (e.g., ".jpg") */
  fileNameSuffix?: string;
  /** Zero-padding digits for frame index (e.g., 3 for 001, 002... default 3) */
  digitPadding?: number;
  /** 1-based indexing (default true, frames 1..N) or 0-based (0..N-1) */
  oneBasedIndex?: boolean;
  /** Scroll scrub duration in pixels (e.g., "+=3000" or 3000, default "+=3000") */
  scrollDistance?: string | number;
  /** Aspect ratio fit mode: "cover" (fills canvas) or "contain" (no crop) */
  fit?: "cover" | "contain";
  /** GSAP scrub smoothness lag (e.g. 0.5 to 1.0, default 0.6) */
  scrub?: number | boolean;
  /** Custom overlay elements (e.g., headlines, badges) positioned over the pinned canvas */
  children?: React.ReactNode;
  /** Custom className for the outer container */
  className?: string;
  /** Callback on load progress (0 - 100) */
  onProgress?: (progress: number) => void;
  /** Callback when all frames finish preloading */
  onLoaded?: () => void;
}

export const ScrollImageSequence: React.FC<ScrollImageSequenceProps> = ({
  frameFolder,
  frameCount,
  fileNamePrefix = "ezgif-frame-",
  fileNameSuffix = ".jpg",
  digitPadding = 3,
  oneBasedIndex = true,
  scrollDistance = "+=3000",
  fit = "cover",
  scrub = 0.6,
  children,
  className = "",
  onProgress,
  onLoaded,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Preloaded HTMLImageElement cache array (indexed 0 to frameCount - 1)
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const currentFrameRef = useRef<{ index: number }>({ index: 0 });
  const lastRenderedIndexRef = useRef<number>(-1);
  const rafIdRef = useRef<number | null>(null);

  // Loading state
  const [loadProgress, setLoadProgress] = useState<number>(0);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  // Format frame number with leading zeroes (e.g. 1 -> "001")
  const getFrameUrl = useCallback(
    (index: number) => {
      const frameNum = oneBasedIndex ? index + 1 : index;
      const paddedNum = String(frameNum).padStart(digitPadding, "0");
      const cleanFolder = frameFolder.endsWith("/")
        ? frameFolder.slice(0, -1)
        : frameFolder;
      return `${cleanFolder}/${fileNamePrefix}${paddedNum}${fileNameSuffix}`;
    },
    [frameFolder, fileNamePrefix, fileNameSuffix, digitPadding, oneBasedIndex]
  );

  // Draw a specific frame onto the canvas with proper aspect ratio handling
  const renderFrame = useCallback(
    (frameIndex: number) => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d", { alpha: false });
      if (!ctx) return;

      const clampedIndex = Math.max(
        0,
        Math.min(frameCount - 1, Math.round(frameIndex))
      );
      const img = imagesRef.current[clampedIndex];
      if (!img || !img.complete || img.naturalWidth === 0) return;

      // Only draw if target frame changed or forced by resize
      lastRenderedIndexRef.current = clampedIndex;

      const cw = canvas.width;
      const ch = canvas.height;
      const iw = img.naturalWidth;
      const ih = img.naturalHeight;

      let drawWidth = cw;
      let drawHeight = ch;
      let offsetX = 0;
      let offsetY = 0;

      if (fit === "cover") {
        const hRatio = cw / iw;
        const vRatio = ch / ih;
        const ratio = Math.max(hRatio, vRatio);
        drawWidth = iw * ratio;
        drawHeight = ih * ratio;
        offsetX = (cw - drawWidth) / 2;
        offsetY = (ch - drawHeight) / 2;
      } else {
        // contain
        const hRatio = cw / iw;
        const vRatio = ch / ih;
        const ratio = Math.min(hRatio, vRatio);
        drawWidth = iw * ratio;
        drawHeight = ih * ratio;
        offsetX = (cw - drawWidth) / 2;
        offsetY = (ch - drawHeight) / 2;
      }

      ctx.clearRect(0, 0, cw, ch);
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
    },
    [frameCount, fit]
  );

  // Resize canvas to match display pixel size & device pixel ratio
  const handleResize = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2); // Cap at 2x for GPU performance

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;

    // Redraw current active frame immediately on resize
    renderFrame(currentFrameRef.current.index);
  }, [renderFrame]);

  // 1. Preload all frames sequentially into memory cache
  useEffect(() => {
    let isCancelled = false;
    let loadedCount = 0;
    imagesRef.current = new Array(frameCount);

    const checkAllLoaded = () => {
      loadedCount++;
      const progress = Math.round((loadedCount / frameCount) * 100);
      if (!isCancelled) {
        setLoadProgress(progress);
        onProgress?.(progress);

        if (loadedCount >= frameCount) {
          setIsLoaded(true);
          onLoaded?.();
        }
      }
    };

    for (let i = 0; i < frameCount; i++) {
      const img = new Image();
      img.src = getFrameUrl(i);
      img.onload = checkAllLoaded;
      img.onerror = () => {
        console.warn(`[ScrollImageSequence] Failed to load frame: ${img.src}`);
        checkAllLoaded(); // Don't block sequence on individual missing frame
      };
      imagesRef.current[i] = img;
    }

    return () => {
      isCancelled = true;
    };
  }, [frameCount, getFrameUrl, onProgress, onLoaded]);

  // 2. Initialize Canvas dimensions and GSAP ScrollTrigger once preloading completes
  useEffect(() => {
    if (!isLoaded) return;

    // Set initial canvas resolution
    handleResize();

    // Draw initial frame (frame 0)
    renderFrame(0);

    const container = containerRef.current;
    if (!container) return;

    // GSAP context for clean scoped animation and automatic teardown
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: container,
          start: "top top",
          end: typeof scrollDistance === "number" ? `+=${scrollDistance}` : scrollDistance,
          pin: true,
          pinSpacing: true,
          scrub: scrub,
          anticipatePin: 1,
          onUpdate: (self) => {
            // Map scroll progress (0..1) linearly to frame index (0..frameCount - 1)
            const targetFrame = self.progress * (frameCount - 1);
            currentFrameRef.current.index = targetFrame;

            const rounded = Math.round(targetFrame);
            if (rounded !== lastRenderedIndexRef.current) {
              if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
              rafIdRef.current = requestAnimationFrame(() => {
                renderFrame(rounded);
              });
            }
          },
        },
      });

      // Track timeline reference
      tl.to({}, { duration: 1 });
    }, containerRef);

    // Debounced window resize listener
    let resizeTimer: NodeJS.Timeout;
    const onWindowResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        handleResize();
        ScrollTrigger.refresh();
      }, 150);
    };

    window.addEventListener("resize", onWindowResize);

    return () => {
      if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
      window.removeEventListener("resize", onWindowResize);
      ctx.revert(); // Automatically kills all ScrollTriggers in context
    };
  }, [isLoaded, frameCount, scrollDistance, scrub, handleResize, renderFrame]);

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-screen overflow-hidden bg-[#0A0D14] select-none ${className}`}
      style={{ willChange: "transform" }}
    >
      {/* ─── LOADING FALLBACK OVERLAY ─── */}
      {!isLoaded && (
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-[#0A0D14] text-white p-6 transition-opacity duration-500">
          <div className="relative w-64 max-w-full">
            {/* Spinning Ring */}
            <div className="w-16 h-16 mx-auto mb-6 relative">
              <div className="w-full h-full border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center font-mono text-xs text-cyan-300 font-bold">
                {loadProgress}%
              </div>
            </div>

            <div className="text-center mb-4">
              <h4 className="text-sm font-bold tracking-widest uppercase text-slate-200">
                Preloading Sequence
              </h4>
              <p className="text-xs text-slate-400 mt-1 font-mono">
                Decaching {frameCount} high-res frames...
              </p>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full transition-all duration-150 ease-out shadow-[0_0_10px_rgba(6,182,212,0.6)]"
                style={{ width: `${loadProgress}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ─── HTML5 CANVAS STAGE ─── */}
      <canvas
        ref={canvasRef}
        className="w-full h-full block object-cover"
        style={{ willChange: "transform" }}
      />

      {/* ─── DYNAMIC OVERLAY CONTENT / CHILDREN ─── */}
      {isLoaded && children && (
        <div className="absolute inset-0 pointer-events-none z-20 flex flex-col justify-between p-6 md:p-12">
          {children}
        </div>
      )}
    </div>
  );
};
export default ScrollImageSequence;
