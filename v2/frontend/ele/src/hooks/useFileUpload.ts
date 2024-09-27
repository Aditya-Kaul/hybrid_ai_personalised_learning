import { useState, ChangeEvent } from 'react'
import { processAndGenerateRoadmap } from '../services/api'

export function useFileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [keyConcepts, setKeyConcepts] = useState<string[]>([])
  const [roadmap, setRoadmap] = useState<{ concept: string; completed: boolean }[]>([])

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const uploadFile = async () => {
    if (!file) return

    setUploadStatus('uploading')
    try {
      const result = await processAndGenerateRoadmap(file)
      setKeyConcepts(result.map(item => item.concept))
      setRoadmap(result)
      setUploadStatus('success')
    } catch (error) {
      console.error('Error uploading file:', error)
      setUploadStatus('error')
    }
  }

  return { file, uploadStatus, keyConcepts, roadmap, handleFileChange, uploadFile }
}