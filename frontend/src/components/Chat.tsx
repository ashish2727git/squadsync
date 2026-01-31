import { useState, useEffect, useRef } from 'react'
import './Chat.css'

interface ChatProps {
  socket: WebSocket | null
  userId: string
  username: string
  roomId: string
}

interface ChatMessage {
  id: string
  userId: string
  username: string
  message: string
  timestamp: string
}

export function Chat({ socket, userId, username, roomId }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!socket) return

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'chat_message') {
          setMessages(prev => [...prev, {
            id: data.id || Date.now().toString(),
            userId: data.userId,
            username: data.username,
            message: data.message,
            timestamp: data.timestamp || new Date().toISOString()
          }])
        }
      } catch (err) {
        console.error('Chat message error:', err)
      }
    }

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [socket])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || !socket) return

    socket.send(JSON.stringify({
      type: 'chat_message',
      roomId,
      userId,
      username,
      message: inputMessage.trim(),
      timestamp: new Date().toISOString()
    }))

    setInputMessage('')
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>💬 Squad Chat</h3>
      </div>
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">No messages yet. Start the conversation!</div>
        ) : (
          messages.map(msg => (
            <div 
              key={msg.id} 
              className={`chat-message ${msg.userId === userId ? 'own-message' : ''}`}
            >
              <div className="message-header">
                <span className="message-username">{msg.username}</span>
                <span className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">{msg.message}</div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message..."
          className="chat-input"
        />
        <button type="submit" className="chat-send-btn">
          Send
        </button>
      </form>
    </div>
  )
}
