import { useState, useEffect } from 'react'
import { FileUpload } from '../components/FileUpload'
import AnimatedProcessingSteps from '../components/ProcessingSteps'
import { useFileUpload } from '../hooks/useFileUpload'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type Step = {
  name: string
  status: 'pending' | 'completed' | 'processing'
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
      const formattedRoadmap = roadmap.map(concept => ({ concept, completed: false }))
      navigate('/lesson', {
        state: {
          keyConcepts,
          roadmap: formattedRoadmap,
          initialConcept: keyConcepts[0]
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
      setProcessingSteps(steps => [
        { ...steps[0], status: 'completed' },
        { ...steps[1], status: 'processing' },
        ...steps.slice(2)
      ])
    } else if (uploadStatus === 'success') {
      setProcessingSteps(steps => steps.map((step, index) => {
        if (index === 0) return { ...step, status: 'completed' }
        if (index === 1) return { ...step, status: 'completed' }
        if (index === 2) return { ...step, status: 'processing' }
        return step
      }))
     
      // Simulate the last two steps completing after a delay
      setTimeout(() => {
        setProcessingSteps(steps => steps.map((step, index) => {
          if (index <= 2) return { ...step, status: 'completed' }
          if (index === 3) return { ...step, status: 'processing' }
          return step
        }))
      }, 2000)
      setTimeout(() => {
        setProcessingSteps(steps => steps.map(step => ({ ...step, status: 'completed' })))
      }, 4000)
    }
  }, [uploadStatus])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="font-bold font-sans tracking-wide text-4xl mb-8">
        Hi, Welcome to GenAI learning
      </h1>
      <FileUpload file={file} onFileChange={handleFileChange} onUpload={handleUpload} />
      <AnimatedProcessingSteps steps={processingSteps} />
    </div>
  )
}