import { apiClient } from './client'

export const uploadAPI = {
  uploadAvatar: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/upload/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  uploadSquadLogo: async (squadId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post(`/upload/squad-logo/${squadId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  uploadAttachment: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/upload/attachment', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  deleteFile: async (fileKey: string) => {
    const response = await apiClient.delete('/upload/file', {
      params: { file_key: fileKey },
    })
    return response.data
  },
}
