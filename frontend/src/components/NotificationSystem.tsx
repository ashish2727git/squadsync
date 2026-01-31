import { useState, useEffect } from 'react'
import './NotificationSystem.css'

interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message: string
  timestamp: number
}

let notificationId = 0

export const notificationService = {
  listeners: new Set<(notification: Notification) => void>(),
  
  show(type: Notification['type'], title: string, message: string) {
    const notification: Notification = {
      id: `notif-${++notificationId}`,
      type,
      title,
      message,
      timestamp: Date.now(),
    }
    this.listeners.forEach(listener => listener(notification))
  },
  
  success(title: string, message: string) {
    this.show('success', title, message)
  },
  
  error(title: string, message: string) {
    this.show('error', title, message)
  },
  
  info(title: string, message: string) {
    this.show('info', title, message)
  },
  
  warning(title: string, message: string) {
    this.show('warning', title, message)
  },
}

export function NotificationSystem() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  useEffect(() => {
    const handleNotification = (notification: Notification) => {
      setNotifications(prev => [...prev, notification])
      
      // Auto-remove after 5 seconds
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== notification.id))
      }, 5000)
    }

    notificationService.listeners.add(handleNotification)
    return () => {
      notificationService.listeners.delete(handleNotification)
    }
  }, [])

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return '✓'
      case 'error': return '✕'
      case 'warning': return '⚠'
      case 'info': return 'ℹ'
    }
  }

  return (
    <div className="notification-container">
      {notifications.map(notif => (
        <div key={notif.id} className={`notification notification-${notif.type}`}>
          <div className="notification-icon">{getIcon(notif.type)}</div>
          <div className="notification-content">
            <div className="notification-title">{notif.title}</div>
            <div className="notification-message">{notif.message}</div>
          </div>
          <button className="notification-close" onClick={() => removeNotification(notif.id)}>
            ×
          </button>
        </div>
      ))}
    </div>
  )
}
