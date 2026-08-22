"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export interface ScrollImageSequenceProps {
  frameFolder: string;
  frameCount: number;
  fileNamePrefix?: string;
  fileNameSuffix?: string;
  digitPadding?: number;
  oneBasedIndex?: boolean;
  scrollDistance?: string | number;
  fit?: "cover" | "contain";
  scrub?: number | boolean;
  children?: React.ReactNode;
  className?: string;
  onProgress?: (progress: number) => void;
  onLoaded?: () => void;
}

export const ScrollImageSequence: React.FC<ScrollImageSequenceProps> = ({
  frameFolder,
  frameCount,
  fileNamePrefix = "ezgif-frame-" ,
  fileNameSuffix = ".jpg",
  digitPadding = 3,
  oneBasedIndex = true,
  scrollDistance = 4000,
  fit = "cover",
  scrub = 0.3,
  children,
  className = "",
  onProgress,
  onLoaded,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // In-memory preloaded frame cache
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const currentFrameRef = useRef<number>(0);
  const lastDrawnFrameRef = useRef<number>(-1);
  const rafIdRef = useRef<number | null>(null);

  // Preload progress
  const [loadProgress, setLoadProgress] = useState<number>(0);
  const [isInitialReady, setIsInitialReady] = useState<boolean>(false);

  // Format frame number with leading zeroes (e.g. 0 -> "/sequence/ezgif-frame-001.jpg")
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

  // Render a specific frame onto the canvas
  const renderFrame = useCallback(
    (frameIndex: number) => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d", { alpha: false });
      if (!ctx) return;

      let cw = canvas.width;
      let ch = canvas.height;

      // Guard against zero-sized canvas
      if (cw === 0 || ch === 0) {
        const rect = canvas.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        cw = canvas.width = Math.round((rect.width || window.innerWidth || 1920) * dpr);
        ch = canvas.height = Math.round((rect.height || window.innerHeight || 1080) * dpr);
      }

      const clampedIndex = Math.max(
        0,
        Math.min(frameCount - 1, Math.round(frameIndex))
      );

      // Find current requested frame or best available loaded frame
      let img = imagesRef.current[clampedIndex];
      if (!img || !img.complete || img.naturalWidth === 0) {
        if (lastDrawnFrameRef.current >= 0 && imagesRef.current[lastDrawnFrameRef.current]?.complete) {
          img = imagesRef.current[lastDrawnFrameRef.current];
        } else if (imagesRef.current[0]?.complete && imagesRef.current[0]?.naturalWidth > 0) {
          img = imagesRef.current[0];
        } else {
          // If frame 0 is still loading, find ANY loaded frame
          for (let i = 0; i < frameCount; i++) {
            if (imagesRef.current[i]?.complete && imagesRef.current[i]!.naturalWidth > 0) {
              img = imagesRef.current[i];
              break;
            }
          }
        }
      }

      if (!img || !img.complete || img.naturalWidth === 0) return;

      lastDrawnFrameRef.current = clampedIndex;

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
        const hRatio = cw / iw;
        const vRatio = ch / ih;
        const ratio = Math.min(hRatio, vRatio);
        drawWidth = iw * ratio;
        drawHeight = ih * ratio;
        offsetX = (cw - drawWidth) / 2;
        offsetY = (ch - drawHeight) / 2;
      }

      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.fillStyle = "#06080E";
      ctx.fillRect(0, 0, cw, ch);
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
    },
    [frameCount, fit]
  );

  // Resize canvas resolution to match container bounding rect & DPI
  const handleResize = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1, 2);

    const targetWidth = Math.round((rect.width || window.innerWidth || 1920) * dpr);
    const targetHeight = Math.round((rect.height || window.innerHeight || 1080) * dpr);

    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }

    renderFrame(currentFrameRef.current);
  }, [renderFrame]);

  // 1. Preload Engine: Immediately load Frame 0, then stream all remaining frames
  useEffect(() => {
    let isCancelled = false;

    // Initialize array
    imagesRef.current = new Array(frameCount);

    // Load Frame 0 with highest priority
    const firstImg = new Image();
    firstImg.src = getFrameUrl(0);
    imagesRef.current[0] = firstImg;

    const onFirstFrameLoaded = () => {
      if (isCancelled) return;
      setIsInitialReady(true);
      onLoaded?.();
      handleResize();
      renderFrame(0);
      loadRemainingFrames();
    };

    if (firstImg.complete && firstImg.naturalWidth > 0) {
      onFirstFrameLoaded();
    } else {
      firstImg.onload = onFirstFrameLoaded;
      firstImg.onerror = onFirstFrameLoaded; // Fail-safe
    }

    // Stream remaining frames in batches of 16 for maximum throughput
    let loadedCount = 1;
    const loadRemainingFrames = () => {
      const BATCH_SIZE = 16;
      let idx = 1;

      const loadNextBatch = () => {
        if (isCancelled || idx >= frameCount) return;

        const end = Math.min(frameCount, idx + BATCH_SIZE);
        const promises: Promise<void>[] = [];

        for (let i = idx; i < end; i++) {
          const img = new Image();
          img.src = getFrameUrl(i);
          imagesRef.current[i] = img;

          const p = new Promise<void>((resolve) => {
            if (img.complete && img.naturalWidth > 0) {
              loadedCount++;
              resolve();
            } else {
              img.onload = () => {
                loadedCount++;
                resolve();
              };
              img.onerror = () => {
                loadedCount++;
                resolve();
              };
            }
          });
          promises.push(p);
        }

        Promise.all(promises).then(() => {
          if (!isCancelled) {
            const pct = Math.round((loadedCount / frameCount) * 100);
            setLoadProgress(pct);
            idx = end;
            if (idx < frameCount) {
              setTimeout(loadNextBatch, 5);
            }
          }
        });
      };

      loadNextBatch();
    };

    return () => {
      isCancelled = true;
    };
  }, [frameCount, getFrameUrl, onLoaded, handleResize, renderFrame]);

  // 2. Setup GSAP ScrollTrigger and ResizeObserver
  useEffect(() => {
    handleResize();
    renderFrame(0);

    const container = containerRef.current;
    if (!container) return;

    // ResizeObserver to ensure canvas size is ALWAYS up to date
    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });
    resizeObserver.observe(container);

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
            const scrollPct = Math.round(self.progress * 100);
            onProgress?.(scrollPct);

            const targetFrame = self.progress * (frameCount - 1);
            currentFrameRef.current = targetFrame;

            const rounded = Math.round(targetFrame);
            if (rounded !== lastDrawnFrameRef.current) {
              if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
              rafIdRef.current = requestAnimationFrame(() => {
                renderFrame(rounded);
              });
            }
          },
        },
      });

      tl.to({}, { duration: 1 });
    }, containerRef);

    const onWindowResize = () => {
      handleResize();
      ScrollTrigger.refresh();
    };

    window.addEventListener("resize", onWindowResize);

    return () => {
      resizeObserver.disconnect();
      if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
      window.removeEventListener("resize", onWindowResize);
      ctx.revert();
    };
  }, [frameCount, scrollDistance, scrub, handleResize, renderFrame, onProgress]);

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-screen overflow-hidden bg-[#06080E] select-none ${className}`}
      style={{ willChange: "transform" }}
    >
      {/* HTML5 Canvas Stage */}
      <canvas
        ref={canvasRef}
        className="w-full h-full block object-cover"
        style={{ willChange: "transform" }}
      />

      {/* Subtle Background Preload Progress Pill */}
      {loadProgress < 100 && (
        <div className="absolute top-20 right-6 z-30 pointer-events-none opacity-60 hover:opacity-100 transition-opacity">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-white/10 text-[10px] font-mono text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            <span>Caching 3D: {loadProgress}%</span>
          </div>
        </div>
      )}

      {/* Dynamic Overlay Content / Children */}
      {children && (
        <div className="absolute inset-0 pointer-events-none z-20 flex flex-col justify-between">
          {children}
        </div>
      )}
    </div>
  );
};

export default ScrollImageSequence;
