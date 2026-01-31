import { useState, useRef } from 'react'
import { uploadAPI } from '../api/upload'
import './AvatarUpload.css'

interface AvatarUploadProps {
  currentAvatar?: string
  onSuccess?: (url: string) => void
}

export function AvatarUpload({ currentAvatar, onSuccess }: AvatarUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [preview, setPreview] = useState<string | null>(currentAvatar || null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('File too large. Max 5MB')
      return
    }

    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    setUploading(true)
    try {
      const response = await uploadAPI.uploadAvatar(file)
      if (response.success) {
        onSuccess?.(response.avatar_url)
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Upload failed')
      setPreview(currentAvatar || null)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="avatar-upload">
      <div className="avatar-preview" onClick={() => fileInputRef.current?.click()}>
        {preview ? (
          <img src={preview} alt="Avatar" />
        ) : (
          <div className="avatar-placeholder">
            <span>📷</span>
            <span>Upload</span>
          </div>
        )}
        {uploading && (
          <div className="avatar-uploading">
            <div className="spinner"></div>
          </div>
        )}
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      <p className="avatar-hint">Click to upload (max 5MB)</p>
    </div>
  )
}
