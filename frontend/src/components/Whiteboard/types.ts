/**
 * Type definitions for Whiteboard component
 */

export interface Point {
  x: number;
  y: number;
}

export interface DrawingPath {
  id: string;
  userId: string;
  username: string;
  color: string;
  lineWidth: number;
  points: Point[];
  timestamp: number;
}

export interface DrawingEvent {
  type: 'draw_start' | 'draw_move' | 'draw_end' | 'clear';
  pathId?: string;
  userId: string;
  username: string;
  color: string;
  lineWidth: number;
  point?: Point;
  timestamp: number;
}

export interface WhiteboardState {
  paths: Map<string, DrawingPath>;
  currentPath: DrawingPath | null;
  isDrawing: boolean;
  backgroundImage: HTMLImageElement | null;
}

export interface WhiteboardProps {
  socket: WebSocket;
  userId: string;
  username: string;
  width?: number;
  height?: number;
  strokeColor?: string;
  strokeWidth?: number;
  backgroundImageUrl?: string;
  onBackgroundImageLoad?: (image: HTMLImageElement) => void;
  className?: string;
}

export interface DrawingConfig {
  color: string;
  lineWidth: number;
}
