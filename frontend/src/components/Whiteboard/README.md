# Whiteboard Component

Production-ready React whiteboard component with real-time WebSocket synchronization.

## Features

- ✅ Canvas-based drawing using native Canvas API
- ✅ Real-time synchronization via WebSocket
- ✅ Support for drawing over uploaded images (game maps)
- ✅ Clean separation of drawing logic and socket logic
- ✅ Event throttling to reduce bandwidth usage
- ✅ Touch and mouse support
- ✅ High DPI display support
- ✅ TypeScript support

## Installation

The component is self-contained and requires no external drawing libraries.

## Usage

```tsx
import React, { useState, useEffect } from 'react';
import { Whiteboard } from './components/Whiteboard';

function App() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const userId = 'user-123';
  const username = 'PlayerOne';

  useEffect(() => {
    // Connect to WebSocket (assumes authenticated)
    const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  if (!socket || socket.readyState !== WebSocket.OPEN) {
    return <div>Connecting to server...</div>;
  }

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Whiteboard
        socket={socket}
        userId={userId}
        username={username}
        width={1200}
        height={800}
        strokeColor="#000000"
        strokeWidth={3}
        backgroundImageUrl="https://example.com/game-map.png"
        onBackgroundImageLoad={(img) => {
          console.log('Background image loaded:', img.width, 'x', img.height);
        }}
      />
    </div>
  );
}
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `socket` | `WebSocket` | Yes | - | Authenticated WebSocket connection |
| `userId` | `string` | Yes | - | Current user's unique identifier |
| `username` | `string` | Yes | - | Current user's display name |
| `width` | `number` | No | `800` | Canvas width in pixels |
| `height` | `number` | No | `600` | Canvas height in pixels |
| `strokeColor` | `string` | No | `"#000000"` | Default stroke color (hex) |
| `strokeWidth` | `number` | No | `2` | Default stroke width in pixels |
| `backgroundImageUrl` | `string` | No | - | URL of background image (game map) |
| `onBackgroundImageLoad` | `(img: HTMLImageElement) => void` | No | - | Callback when background image loads |
| `className` | `string` | No | `""` | Additional CSS class names |

## WebSocket Protocol

The component sends and receives JSON messages over WebSocket:

### Outgoing Events (Client → Server)

```typescript
// Drawing start
{
  type: 'draw_start',
  pathId: string,
  userId: string,
  username: string,
  color: string,
  lineWidth: number,
  point: { x: number, y: number },
  timestamp: number
}

// Drawing move (throttled to ~60fps)
{
  type: 'draw_move',
  pathId: string,
  userId: string,
  username: string,
  point: { x: number, y: number },
  timestamp: number
}

// Drawing end
{
  type: 'draw_end',
  pathId: string,
  userId: string,
  username: string,
  timestamp: number
}

// Clear canvas
{
  type: 'clear',
  userId: string,
  username: string,
  timestamp: number
}
```

### Incoming Events (Server → Client)

The component expects the same event types from the server to sync remote drawings.

## Architecture

The component is structured with clear separation of concerns:

- **`Whiteboard.tsx`**: Main component, orchestrates drawing and sync
- **`hooks/useDrawing.ts`**: Pure drawing logic (no socket dependencies)
- **`hooks/useWhiteboardSync.ts`**: WebSocket communication (no drawing dependencies)
- **`utils/throttle.ts`**: Event throttling utilities
- **`types.ts`**: TypeScript type definitions

## Performance Optimizations

1. **Event Throttling**: Drawing move events are throttled to ~60fps (16ms intervals)
2. **Incremental Drawing**: Remote paths are drawn incrementally, not redrawn from scratch
3. **High DPI Support**: Canvas is properly scaled for retina displays
4. **Efficient Redraws**: Only affected paths are redrawn, not the entire canvas

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Notes

- The component assumes the WebSocket connection is already authenticated
- Background images are loaded with CORS support (`crossOrigin="anonymous"`)
- The canvas automatically scales to fit its container
- Touch events are supported for mobile devices
