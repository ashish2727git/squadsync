# Summon Modal Component

Tactical, urgent modal component for SquadSync summons that cannot be ignored.

## Features

- ✅ **Instant Display**: Pops immediately when summon is received
- ✅ **Cannot Be Ignored**: Blocks all interaction, no close button, ESC disabled
- ✅ **ACCEPT/DECLINE Only**: Tactical response options (no MAYBE)
- ✅ **API Integration**: Sends response via REST API
- ✅ **Closes After Response**: Only closes when user submits response
- ✅ **Tactical UI**: Urgent, military-style design with pulsing alerts
- ✅ **Mobile-Friendly**: Responsive design for all screen sizes
- ✅ **Real-time**: Integrates with WebSocket notifications

## Usage

```tsx
import React, { useState, useCallback } from 'react';
import { SummonModal } from './components/SummonModal';
import { useSummonListener } from './components/SummonModal/useSummonListener';
import { SummonData } from './components/SummonModal/types';

function App() {
  const socket = useWebSocket(); // Your WebSocket connection
  const userId = 'user-123';
  const apiBaseUrl = 'http://localhost:8000';
  const authToken = 'your-jwt-token';
  
  const [currentSummon, setCurrentSummon] = useState<SummonData | null>(null);

  const handleSummonReceived = useCallback((summon: SummonData) => {
    setCurrentSummon(summon);
  }, []);

  const handleResponseSubmitted = useCallback((summonId: string, response: 'ACCEPT' | 'DECLINE') => {
    setCurrentSummon(null);
    console.log(`Responded ${response} to summon ${summonId}`);
  }, []);

  // Listen for summon notifications
  useSummonListener({
    socket,
    userId,
    onSummonReceived: handleSummonReceived,
  });

  return (
    <div>
      {/* Your app content */}
      
      {currentSummon && (
        <SummonModal
          summon={currentSummon}
          userId={userId}
          apiBaseUrl={apiBaseUrl}
          authToken={authToken}
          onResponseSubmitted={handleResponseSubmitted}
          onError={(error) => console.error('Summon error:', error)}
        />
      )}
    </div>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `summon` | `SummonData` | Yes | Summon data object |
| `userId` | `string` | Yes | Current user's ID |
| `apiBaseUrl` | `string` | Yes | Base URL for API (e.g., "http://localhost:8000") |
| `authToken` | `string` | Yes | JWT authentication token |
| `onResponseSubmitted` | `(summonId: string, response: 'ACCEPT' \| 'DECLINE') => void` | Yes | Callback when response is submitted |
| `onError` | `(error: Error) => void` | No | Error handler callback |

## SummonData Interface

```typescript
interface SummonData {
  id: string;
  squad_id: string;
  squad_name: string;
  created_by_id: string;
  created_by_username: string;
  title: string;
  description?: string;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'EXPIRED' | 'CANCELLED';
  expires_at?: string; // ISO 8601 datetime string
  created_at: string; // ISO 8601 datetime string
}
```

## Behavior

### Cannot Be Ignored
- **No close button**: Modal has no X button or close option
- **ESC disabled**: Escape key is prevented from closing
- **Click outside disabled**: Clicking overlay does nothing
- **Blocks interaction**: All other UI is blocked by overlay
- **Body scroll locked**: Prevents scrolling when modal is open

### Response Required
- Modal only closes after user clicks ACCEPT or DECLINE
- Response is sent immediately to API
- Loading state shown during submission
- Error handling with retry capability

### Visual Design
- **Tactical color scheme**: Dark background with orange/red accents
- **Pulsing alerts**: Animated alert indicator
- **Countdown timer**: Shows time remaining if expires_at is set
- **Urgent typography**: Bold, uppercase text
- **Mobile optimized**: Full-screen on mobile devices

## WebSocket Integration

The component works with WebSocket notifications. Use the `useSummonListener` hook:

```tsx
useSummonListener({
  socket: websocket,
  userId: 'user-123',
  onSummonReceived: (summon) => {
    // Show modal
    setCurrentSummon(summon);
  },
});
```

The hook listens for messages with `event_type: 'summon_created'` and extracts summon data.

## API Integration

The component sends POST requests to:
```
POST {apiBaseUrl}/api/v1/summons/{summon_id}/respond
```

Request body:
```json
{
  "response_type": "ACCEPT" | "DECLINE",
  "message": null
}
```

Headers:
```
Authorization: Bearer {authToken}
Content-Type: application/json
```

## Styling

The component uses CSS modules with:
- Dark tactical theme
- Orange/red urgent accents
- Smooth animations
- Responsive breakpoints
- Mobile-first design

## Accessibility

- `role="dialog"` and `aria-modal="true"` for screen readers
- `aria-labelledby` pointing to title
- `aria-label` on buttons
- Keyboard navigation support (though ESC is disabled by design)

## Browser Support

- Chrome/Edge (latest) ✅
- Firefox (latest) ✅
- Safari (latest) ✅
- Mobile browsers ✅
