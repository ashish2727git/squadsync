/**
 * Drawing logic hook - handles all canvas drawing operations
 * Separated from socket logic for clean architecture
 */

import { useCallback, useRef } from 'react';
import { DrawingPath, Point, DrawingConfig } from '../types';
import { generatePathId } from '../utils/idGenerator';

interface UseDrawingOptions {
  onPathStart?: (path: DrawingPath) => void;
  onPathUpdate?: (path: DrawingPath) => void;
  onPathComplete?: (path: DrawingPath) => void;
}

/**
 * Hook for managing drawing operations on canvas
 */
export function useDrawing(
  canvasRef: React.RefObject<HTMLCanvasElement>,
  config: DrawingConfig,
  options: UseDrawingOptions = {}
) {
  const { onPathStart, onPathUpdate, onPathComplete } = options;
  const currentPathRef = useRef<DrawingPath | null>(null);
  const isDrawingRef = useRef(false);

  /**
   * Get point coordinates relative to canvas
   */
  const getPointFromEvent = useCallback((e: React.MouseEvent<HTMLCanvasElement> | MouseEvent | TouchEvent): Point | null => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    let clientX: number;
    let clientY: number;

    if ('touches' in e) {
      // Touch event
      if (e.touches.length === 0) return null;
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      // Mouse event
      clientX = e.clientX;
      clientY = e.clientY;
    }

    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  }, [canvasRef]);

  /**
   * Draw a single point on the canvas
   */
  const drawPoint = useCallback((ctx: CanvasRenderingContext2D, point: Point, color: string, lineWidth: number) => {
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(point.x, point.y, lineWidth / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }, []);

  /**
   * Draw a line between two points
   */
  const drawLine = useCallback((
    ctx: CanvasRenderingContext2D,
    from: Point,
    to: Point,
    color: string,
    lineWidth: number
  ) => {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
    ctx.restore();
  }, []);

  /**
   * Redraw the entire canvas
   */
  const redrawCanvas = useCallback((paths: DrawingPath[], backgroundImage: HTMLImageElement | null = null) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background image if present
    if (backgroundImage) {
      ctx.drawImage(backgroundImage, 0, 0, canvas.width, canvas.height);
    }

    // Draw all paths
    paths.forEach((path) => {
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
  }, [canvasRef, drawLine]);

  /**
   * Start drawing a new path
   */
  const startDrawing = useCallback((point: Point, userId: string, username: string) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    isDrawingRef.current = true;

    const newPath: DrawingPath = {
      id: generatePathId(),
      userId,
      username,
      color: config.color,
      lineWidth: config.lineWidth,
      points: [point],
      timestamp: Date.now(),
    };

    currentPathRef.current = newPath;

    // Draw initial point
    const ctx = canvas.getContext('2d');
    if (ctx) {
      drawPoint(ctx, point, config.color, config.lineWidth);
    }

    onPathStart?.(newPath);
  }, [config, drawPoint, onPathStart]);

  /**
   * Continue drawing current path
   */
  const continueDrawing = useCallback((point: Point) => {
    const canvas = canvasRef.current;
    const currentPath = currentPathRef.current;

    if (!canvas || !currentPath || !isDrawingRef.current) return;

    const previousPoint = currentPath.points[currentPath.points.length - 1];
    currentPath.points.push(point);

    // Draw line from previous point to current point
    const ctx = canvas.getContext('2d');
    if (ctx) {
      drawLine(ctx, previousPoint, point, config.color, config.lineWidth);
    }

    onPathUpdate?.(currentPath);
  }, [config, drawLine, onPathUpdate]);

  /**
   * Complete current drawing path
   */
  const stopDrawing = useCallback(() => {
    if (!isDrawingRef.current) return;

    const currentPath = currentPathRef.current;
    isDrawingRef.current = false;

    if (currentPath) {
      onPathComplete?.(currentPath);
      currentPathRef.current = null;
    }
  }, [onPathComplete]);

  /**
   * Clear the canvas
   */
  const clearCanvas = useCallback((backgroundImage: HTMLImageElement | null = null) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (backgroundImage) {
      ctx.drawImage(backgroundImage, 0, 0, canvas.width, canvas.height);
    }
  }, [canvasRef]);

  /**
   * Draw a complete path on the canvas
   */
  const drawPath = useCallback((path: DrawingPath) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx || path.points.length === 0) return;

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
  }, [canvasRef]);

  /**
   * Draw a line on the canvas (exported for use in component)
   */
  const drawLineOnCanvas = useCallback((
    from: Point,
    to: Point,
    color: string,
    lineWidth: number
  ) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    drawLine(ctx, from, to, color, lineWidth);
  }, [drawLine]);

  return {
    startDrawing,
    continueDrawing,
    stopDrawing,
    clearCanvas,
    drawPath,
    drawLine: drawLineOnCanvas,
    redrawCanvas,
    getPointFromEvent,
    isDrawing: () => isDrawingRef.current,
    currentPath: () => currentPathRef.current,
  };
}
