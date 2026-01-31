import { useEffect, useRef, useState } from 'react'
import './Whiteboard.css'

interface WhiteboardProps {
  socket: WebSocket
  userId: string
  username: string
  width: number
  height: number
}

interface DrawAction {
  type: 'draw' | 'clear'
  x?: number
  y?: number
  prevX?: number
  prevY?: number
  color?: string
  lineWidth?: number
  userId?: string
  username?: string
}

export function Whiteboard({ socket, userId, username, width, height }: WhiteboardProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [color, setColor] = useState('#000000')
  const [lineWidth, setLineWidth] = useState(3)
  const [lastPos, setLastPos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    if (!socket) return

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [socket, color, lineWidth])

  const handleMessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'whiteboard_draw') {
        drawRemote(data.action)
      } else if (data.type === 'whiteboard_clear') {
        clearCanvas()
      }
    } catch (err) {
      console.error('Whiteboard message error:', err)
    }
  }

  const drawRemote = (action: DrawAction) => {
    if (!canvasRef.current || action.userId === userId) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return

    ctx.strokeStyle = action.color || '#000000'
    ctx.lineWidth = action.lineWidth || 3
    ctx.lineCap = 'round'

    ctx.beginPath()
    ctx.moveTo(action.prevX!, action.prevY!)
    ctx.lineTo(action.x!, action.y!)
    ctx.stroke()
  }

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true)
    const pos = getPosition(e)
    setLastPos(pos)
  }

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing || !canvasRef.current) return
    
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return

    const pos = getPosition(e)

    ctx.strokeStyle = color
    ctx.lineWidth = lineWidth
    ctx.lineCap = 'round'

    ctx.beginPath()
    ctx.moveTo(lastPos.x, lastPos.y)
    ctx.lineTo(pos.x, pos.y)
    ctx.stroke()

    socket.send(JSON.stringify({
      type: 'whiteboard_draw',
      action: {
        type: 'draw',
        x: pos.x,
        y: pos.y,
        prevX: lastPos.x,
        prevY: lastPos.y,
        color,
        lineWidth,
        userId,
        username
      }
    }))

    setLastPos(pos)
  }

  const stopDrawing = () => {
    setIsDrawing(false)
  }

  const getPosition = (e: React.MouseEvent | React.TouchEvent) => {
    if (!canvasRef.current) return { x: 0, y: 0 }
    
    const rect = canvasRef.current.getBoundingClientRect()
    
    if ('touches' in e) {
      return {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top
      }
    }
    
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    }
  }

  const clearCanvas = () => {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, width, height)
  }

  const handleClear = () => {
    clearCanvas()
    socket.send(JSON.stringify({
      type: 'whiteboard_clear',
      userId
    }))
  }

  return (
    <div className="whiteboard-container">
      <div className="whiteboard-controls">
        <div className="control-group">
          <label>Color:</label>
          <input
            type="color"
            value={color}
            onChange={(e) => setColor(e.target.value)}
          />
        </div>
        <div className="control-group">
          <label>Width:</label>
          <input
            type="range"
            min="1"
            max="20"
            value={lineWidth}
            onChange={(e) => setLineWidth(Number(e.target.value))}
          />
          <span>{lineWidth}px</span>
        </div>
        <button className="btn-clear" onClick={handleClear}>
          Clear Board
        </button>
      </div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={startDrawing}
        onTouchMove={draw}
        onTouchEnd={stopDrawing}
        className="whiteboard-canvas"
      />
    </div>
  )
}
