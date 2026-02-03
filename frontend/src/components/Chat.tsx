import { useState, useEffect, useRef, useCallback } from 'react'
import './Chat.css'

interface ChatProps {
  socket: WebSocket | null
  userId: string
  username: string
  roomId: string
}

interface Reaction {
  emoji: string
  count: number
  users: string[]
}

interface ChatMessage {
  id: string
  userId: string
  username: string
  message: string
  timestamp: string
  isEdited?: boolean
  isPinned?: boolean
  replyTo?: string
  reactions?: Reaction[]
}

interface TypingUser {
  userId: string
  username: string
}

const EMOJI_LIST = ['👍', '❤️', '😂', '😮', '😢', '🔥', '🎮', '💯', '👏', '🚀']

export function Chat({ socket, userId, username, roomId }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([])
  const [showEmojiPicker, setShowEmojiPicker] = useState<string | null>(null)
  const [replyingTo, setReplyingTo] = useState<ChatMessage | null>(null)
  const [editingMessage, setEditingMessage] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const typingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const lastTypingSentRef = useRef<number>(0)

  // Load message history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setIsLoadingHistory(true)
        const token = localStorage.getItem('access_token')
        // Try to get channel for this squad
        const channelRes = await fetch(`http://localhost:8000/api/v1/messages/channels/${roomId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (channelRes.ok) {
          const channels = await channelRes.json()
          if (channels.length > 0) {
            const historyRes = await fetch(
              `http://localhost:8002/api/v1/messages/channel/${channels[0].id}?limit=50`,
              { headers: { Authorization: `Bearer ${token}` } }
            )
            if (historyRes.ok) {
              const history = await historyRes.json()
              setMessages(history.map((m: any) => ({
                id: m.id,
                userId: m.sender_id,
                username: m.sender_username || 'Unknown',
                message: m.content,
                timestamp: m.created_at,
                isEdited: m.is_edited,
                isPinned: m.is_pinned,
                reactions: []
              })))
            }
          }
        }
      } catch (err) {
        console.log('Could not load message history')
      } finally {
        setIsLoadingHistory(false)
      }
    }
    loadHistory()
  }, [roomId])

  useEffect(() => {
    if (!socket) return

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'chat_message') {
          const newMsg: ChatMessage = {
            id: data.id || Date.now().toString(),
            userId: data.userId,
            username: data.username,
            message: data.message,
            timestamp: data.timestamp || new Date().toISOString(),
            reactions: []
          }
          setMessages(prev => [...prev, newMsg])
          // Clear typing indicator for this user
          setTypingUsers(prev => prev.filter(u => u.userId !== data.userId))
        }
        
        if (data.type === 'typing_start') {
          if (data.user_id !== userId) {
            setTypingUsers(prev => {
              if (prev.find(u => u.userId === data.user_id)) return prev
              return [...prev, { userId: data.user_id, username: data.username }]
            })
          }
        }
        
        if (data.type === 'typing_stop') {
          setTypingUsers(prev => prev.filter(u => u.userId !== data.user_id))
        }

        if (data.type === 'message_reaction') {
          setMessages(prev => prev.map(msg => {
            if (msg.id === data.message_id) {
              const reactions = msg.reactions || []
              const existing = reactions.find(r => r.emoji === data.emoji)
              if (data.action === 'add') {
                if (existing) {
                  existing.count++
                  existing.users.push(data.user_id)
                } else {
                  reactions.push({ emoji: data.emoji, count: 1, users: [data.user_id] })
                }
              } else if (data.action === 'remove' && existing) {
                existing.count--
                existing.users = existing.users.filter(u => u !== data.user_id)
                if (existing.count <= 0) {
                  const idx = reactions.indexOf(existing)
                  reactions.splice(idx, 1)
                }
              }
              return { ...msg, reactions: [...reactions] }
            }
            return msg
          }))
        }

        if (data.type === 'message_edited') {
          setMessages(prev => prev.map(msg =>
            msg.id === data.message_id
              ? { ...msg, message: data.content, isEdited: true }
              : msg
          ))
        }

        if (data.type === 'message_deleted') {
          setMessages(prev => prev.map(msg =>
            msg.id === data.message_id
              ? { ...msg, message: '[Message deleted]' }
              : msg
          ))
        }
      } catch (err) {
        console.error('Chat message error:', err)
      }
    }

    socket.addEventListener('message', handleMessage)
    return () => socket.removeEventListener('message', handleMessage)
  }, [socket, userId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Clear typing users after 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setTypingUsers([])
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const sendTypingIndicator = useCallback(() => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return
    const now = Date.now()
    if (now - lastTypingSentRef.current < 2000) return
    lastTypingSentRef.current = now

    socket.send(JSON.stringify({
      type: 'typing_start',
      channel_id: roomId
    }))

    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current)
    typingTimeoutRef.current = setTimeout(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'typing_stop',
          channel_id: roomId
        }))
      }
    }, 3000)
  }, [socket, roomId])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputMessage(e.target.value)
    if (e.target.value.trim()) {
      sendTypingIndicator()
    }
  }

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || !socket) return

    if (socket.readyState === WebSocket.OPEN) {
      const messageData: any = {
        type: 'chat_message',
        roomId,
        userId,
        username,
        message: inputMessage.trim(),
        timestamp: new Date().toISOString()
      }
      
      if (replyingTo) {
        messageData.replyTo = replyingTo.id
      }

      socket.send(JSON.stringify(messageData))
      
      // Stop typing indicator
      socket.send(JSON.stringify({ type: 'typing_stop', channel_id: roomId }))
      
      setInputMessage('')
      setReplyingTo(null)
    }
  }

  const addReaction = (messageId: string, emoji: string) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return
    
    socket.send(JSON.stringify({
      type: 'message_reaction',
      message_id: messageId,
      emoji,
      action: 'add',
      channel_id: roomId
    }))
    setShowEmojiPicker(null)
  }

  const startEdit = (msg: ChatMessage) => {
    setEditingMessage(msg.id)
    setEditContent(msg.message)
  }

  const cancelEdit = () => {
    setEditingMessage(null)
    setEditContent('')
  }

  const saveEdit = (messageId: string) => {
    if (!editContent.trim()) return
    // TODO: Send edit via API
    setMessages(prev => prev.map(msg =>
      msg.id === messageId ? { ...msg, message: editContent, isEdited: true } : msg
    ))
    cancelEdit()
  }

  const deleteMessage = (messageId: string) => {
    // TODO: Send delete via API
    setMessages(prev => prev.map(msg =>
      msg.id === messageId ? { ...msg, message: '[Message deleted]' } : msg
    ))
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>💬 Squad Chat</h3>
        <span className="online-count">{messages.length} messages</span>
      </div>
      
      <div className="chat-messages">
        {isLoadingHistory && (
          <div className="loading-history">Loading messages...</div>
        )}
        
        {messages.length === 0 && !isLoadingHistory ? (
          <div className="chat-empty">
            <div className="empty-icon">💬</div>
            <p>No messages yet</p>
            <span>Start the conversation!</span>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const showAvatar = idx === 0 || messages[idx - 1]?.userId !== msg.userId
            return (
              <div 
                key={msg.id} 
                className={`chat-message ${msg.userId === userId ? 'own-message' : ''} ${showAvatar ? 'with-avatar' : 'grouped'}`}
              >
                {showAvatar && (
                  <div className="message-avatar">
                    {msg.username.charAt(0).toUpperCase()}
                  </div>
                )}
                
                <div className="message-body">
                  {showAvatar && (
                    <div className="message-header">
                      <span className="message-username">{msg.username}</span>
                      <span className="message-time">{formatTime(msg.timestamp)}</span>
                      {msg.isEdited && <span className="edited-tag">(edited)</span>}
                      {msg.isPinned && <span className="pinned-tag">📌</span>}
                    </div>
                  )}
                  
                  {editingMessage === msg.id ? (
                    <div className="edit-container">
                      <input
                        type="text"
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        autoFocus
                      />
                      <div className="edit-actions">
                        <button onClick={() => saveEdit(msg.id)}>Save</button>
                        <button onClick={cancelEdit}>Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <div className="message-content">{msg.message}</div>
                  )}
                  
                  {msg.reactions && msg.reactions.length > 0 && (
                    <div className="message-reactions">
                      {msg.reactions.map(r => (
                        <span 
                          key={r.emoji} 
                          className={`reaction ${r.users.includes(userId) ? 'own-reaction' : ''}`}
                          onClick={() => addReaction(msg.id, r.emoji)}
                        >
                          {r.emoji} {r.count}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="message-actions">
                  <button 
                    className="action-btn" 
                    onClick={() => setShowEmojiPicker(showEmojiPicker === msg.id ? null : msg.id)}
                    title="Add reaction"
                  >
                    😀
                  </button>
                  <button 
                    className="action-btn" 
                    onClick={() => setReplyingTo(msg)}
                    title="Reply"
                  >
                    ↩️
                  </button>
                  {msg.userId === userId && (
                    <>
                      <button className="action-btn" onClick={() => startEdit(msg)} title="Edit">✏️</button>
                      <button className="action-btn" onClick={() => deleteMessage(msg.id)} title="Delete">🗑️</button>
                    </>
                  )}
                </div>

                {showEmojiPicker === msg.id && (
                  <div className="emoji-picker">
                    {EMOJI_LIST.map(emoji => (
                      <button key={emoji} onClick={() => addReaction(msg.id, emoji)}>
                        {emoji}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {typingUsers.length > 0 && (
        <div className="typing-indicator">
          <div className="typing-dots">
            <span></span><span></span><span></span>
          </div>
          <span>
            {typingUsers.map(u => u.username).join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
          </span>
        </div>
      )}

      {replyingTo && (
        <div className="reply-preview">
          <span>Replying to <strong>{replyingTo.username}</strong></span>
          <span className="reply-content">{replyingTo.message.substring(0, 50)}...</span>
          <button onClick={() => setReplyingTo(null)}>✕</button>
        </div>
      )}

      <form className="chat-input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={inputMessage}
          onChange={handleInputChange}
          placeholder={replyingTo ? `Reply to ${replyingTo.username}...` : "Type a message... Use @ to mention"}
          className="chat-input"
        />
        <button type="submit" className="chat-send-btn" disabled={!inputMessage.trim()}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </form>
    </div>
  )
}
