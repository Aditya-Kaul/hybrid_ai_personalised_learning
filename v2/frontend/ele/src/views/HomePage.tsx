import { useState, useEffect } from 'react'
import { FileUpload } from '../components/FileUpload'
import { ProcessingSteps } from '../components/ProcessingSteps'
import { useFileUpload } from '../hooks/useFileUpload'
import { useNavigate } from 'react-router-dom'

type Step = {
  name: string
  status: 'pending' | 'completed'
}

export default function HomePage() {
  const { file, uploadStatus, keyConcepts, roadmap, handleFileChange, uploadFile } = useFileUpload()
  const [processingSteps, setProcessingSteps] = useState<Step[]>([
    { name: 'Uploading PDF', status: 'pending' },
    { name: 'Extracting text', status: 'pending' },
    { name: 'Generating key concepts', status: 'pending' },
    { name: 'Creating roadmap', status: 'pending' },
  ])
  const navigate = useNavigate()

  useEffect(() => {
    if (uploadStatus === 'success' && keyConcepts.length > 0 && roadmap.length > 0) {
      // Convert roadmap to the expected format
      const formattedRoadmap = roadmap.map(concept => ({ concept, completed: false }))
      navigate('/lesson', { 
        state: { 
          keyConcepts, 
          roadmap: formattedRoadmap,
          initialConcept: keyConcepts[0] // Pass the first concept as initialConcept
        } 
      })
    }
  }, [uploadStatus, keyConcepts, roadmap, navigate])

  const handleUpload = async () => {
    setProcessingSteps(steps => steps.map(step => ({ ...step, status: 'pending' })))
    await uploadFile()
  }

  useEffect(() => {
    if (uploadStatus === 'uploading') {
      setProcessingSteps(steps => steps.map((step, index) => 
        index <= 1 ? { ...step, status: 'completed' } : step
      ))
    } else if (uploadStatus === 'success') {
      setProcessingSteps(steps => steps.map(step => ({ ...step, status: 'completed' })))
    }
  }, [uploadStatus])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <h1 className="text-4xl font-bold mb-8">Welcome to AI RAG Learning</h1>
      <FileUpload file={file} onFileChange={handleFileChange} onUpload={handleUpload} />
      <ProcessingSteps steps={processingSteps} />
    </div>
  )
}