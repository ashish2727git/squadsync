/**
 * Whiteboard Component
 * Production-ready canvas-based whiteboard with real-time WebSocket sync
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useDrawing } from './hooks/useDrawing';
import { useWhiteboardSync } from './hooks/useWhiteboardSync';
import { WhiteboardProps, DrawingPath, DrawingConfig } from './types';
import './Whiteboard.css';

export const Whiteboard: React.FC<WhiteboardProps> = ({
  socket,
  userId,
  username,
  width = 800,
  height = 600,
  strokeColor = '#000000',
  strokeWidth = 2,
  backgroundImageUrl,
  onBackgroundImageLoad,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [backgroundImage, setBackgroundImage] = useState<HTMLImageElement | null>(null);
  const [drawingConfig, setDrawingConfig] = useState<DrawingConfig>({
    color: strokeColor,
    lineWidth: strokeWidth,
  });
  const [paths, setPaths] = useState<Map<string, DrawingPath>>(new Map());
  const currentPathIdRef = useRef<string | null>(null);
  const pathsRef = useRef<Map<string, DrawingPath>>(new Map());

  // Sync pathsRef with paths state
  useEffect(() => {
    pathsRef.current = paths;
  }, [paths]);

  // Load background image if provided
  useEffect(() => {
    if (!backgroundImageUrl) {
      setBackgroundImage(null);
      return;
    }

    const img = new Image();
    img.crossOrigin = 'anonymous';

    img.onload = () => {
      setBackgroundImage(img);
      onBackgroundImageLoad?.(img);
    };

    img.onerror = () => {
      console.error('Failed to load background image');
      setBackgroundImage(null);
    };

    img.src = backgroundImageUrl;
  }, [backgroundImageUrl, onBackgroundImageLoad]);

  // Initialize canvas size and redraw
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    // Set canvas size based on container or props
    const containerWidth = container.clientWidth || width;
    const containerHeight = container.clientHeight || height;

    // Set display size
    canvas.style.width = `${containerWidth}px`;
    canvas.style.height = `${containerHeight}px`;

    // Set actual size (for high DPI displays)
    const dpr = window.devicePixelRatio || 1;
    const displayWidth = containerWidth;
    const displayHeight = containerHeight;

    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;

    // Scale context for high DPI
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.scale(dpr, dpr);

    // Clear and draw background
    ctx.clearRect(0, 0, displayWidth, displayHeight);
    if (backgroundImage) {
      ctx.drawImage(backgroundImage, 0, 0, displayWidth, displayHeight);
    }

    // Redraw all existing paths
    Array.from(pathsRef.current.values()).forEach((path) => {
      if (path.points.length === 0) return;

      ctx.save();
      ctx.strokeStyle = path.color;
      ctx.lineWidth = path.lineWidth;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      ctx.beginPath();
      const firstPoint = path.points[0];
      ctx.moveTo(firstPoint.x, firstPoint.y);

      for (let i = 1; i < path.points.length; i++) {
        const point = path.points[i];
        ctx.lineTo(point.x, point.y);
      }

      ctx.stroke();
      ctx.restore();
    });
  }, [width, height, backgroundImage]);

  // Handle remote path updates
  const handleRemotePath = useCallback((path: DrawingPath) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    setPaths((prevPaths) => {
      const newPaths = new Map(prevPaths);
      const existingPath = prevPaths.get(path.id);
      newPaths.set(path.id, { ...path });
      
      // Draw incremental updates or full path
      if (path.points.length > 0) {
        ctx.save();
        ctx.strokeStyle = path.color;
        ctx.lineWidth = path.lineWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // Only draw the latest segment if path already exists
        if (existingPath && existingPath.points.length > 0 && existingPath.points.length < path.points.length) {
          // Draw from last point to new points
          const startIndex = existingPath.points.length - 1;
          ctx.beginPath();
          ctx.moveTo(path.points[startIndex].x, path.points[startIndex].y);
          
          for (let i = startIndex + 1; i < path.points.length; i++) {
            ctx.lineTo(path.points[i].x, path.points[i].y);
          }
          
          ctx.stroke();
        } else if (!existingPath || existingPath.points.length === 0) {
          // Draw entire path
          ctx.beginPath();
          const firstPoint = path.points[0];
          ctx.moveTo(firstPoint.x, firstPoint.y);

          for (let i = 1; i < path.points.length; i++) {
            const point = path.points[i];
            ctx.lineTo(point.x, point.y);
          }

          ctx.stroke();
        }
        
        ctx.restore();
      }
      
      return newPaths;
    });
  }, []);

  const handleRemoteClear = useCallback(() => {
    setPaths(new Map());
    drawing.clearCanvas(backgroundImage);
  }, [backgroundImage]);

  // Drawing hook
  const drawing = useDrawing(canvasRef, drawingConfig, {
    onPathStart: (path) => {
      currentPathIdRef.current = path.id;
      sync.broadcastDrawStart(path.id, path.points[0], path.color, path.lineWidth);
    },
    onPathUpdate: (path) => {
      if (currentPathIdRef.current === path.id && path.points.length > 0) {
        const lastPoint = path.points[path.points.length - 1];
        sync.broadcastDrawMove(path.id, lastPoint);
      }
    },
    onPathComplete: (path) => {
      if (currentPathIdRef.current === path.id) {
        sync.broadcastDrawEnd(path.id);
        currentPathIdRef.current = null;
        
        // Add to paths state
        setPaths((prev) => {
          const newPaths = new Map(prev);
          newPaths.set(path.id, path);
          return newPaths;
        });
      }
    },
  });

  // WebSocket sync hook
  const sync = useWhiteboardSync({
    socket,
    userId,
    username,
    onRemotePath: handleRemotePath,
    onRemoteClear: handleRemoteClear,
    throttleMs: 16, // ~60fps
  });

  // Mouse/touch event handlers
const handleStart = useCallback(
  (e: React.PointerEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const point = drawing.getPointFromEvent(e);
    if (point) {
      drawing.startDrawing(point, userId, username);
    }
  },
  [drawing, userId, username]
);


  const handleMove = useCallback(
  (e: React.PointerEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    if (drawing.isDrawing()) {
      const point = drawing.getPointFromEvent(e);
      if (point) {
        drawing.continueDrawing(point);
      }
    }
  },
  [drawing]
);


const handleEnd = useCallback(
  (e: React.PointerEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    drawing.stopDrawing();
  },
  [drawing]
);


  // Handle mouse leave to stop drawing
  const handleLeave = useCallback(() => {
    if (drawing.isDrawing()) {
      drawing.stopDrawing();
    }
  }, [drawing]);

  // Clear canvas handler
  const handleClear = useCallback(() => {
    setPaths(new Map());
    drawing.clearCanvas(backgroundImage);
    sync.broadcastClear();
  }, [drawing, backgroundImage, sync]);

  return (
    <div ref={containerRef} className={`whiteboard-container ${className}`}>
      <div className="whiteboard-controls">
        <div className="whiteboard-toolbar">
          <label>
            Color:
            <input
              type="color"
              value={drawingConfig.color}
              onChange={(e) => setDrawingConfig((prev) => ({ ...prev, color: e.target.value }))}
            />
          </label>
          <label>
            Width:
            <input
              type="range"
              min="1"
              max="20"
              value={drawingConfig.lineWidth}
              onChange={(e) => setDrawingConfig((prev) => ({ ...prev, lineWidth: parseInt(e.target.value, 10) }))}
            />
            <span>{drawingConfig.lineWidth}px</span>
          </label>
          <button onClick={handleClear} className="whiteboard-clear-btn">
            Clear
          </button>
        </div>
      </div>
      <canvas
        ref={canvasRef}
        className="whiteboard-canvas"
        onPointerDown={handleStart}
        onPointerMove={handleMove}
        onPointerUp={handleEnd}
        onPointerLeave={handleLeave}
        style={{
          cursor: 'crosshair',
          touchAction: 'none',
  }}
/>

    </div>
  );
};

export default Whiteboard;
