"use client"

import { useEffect, useState } from 'react'

type Step = {
  name: string
  status: 'pending' | 'completed' | 'processing'
}

type ProcessingStepsProps = {
  steps: Step[]
}

export default function AnimatedProcessingSteps({ steps }: ProcessingStepsProps) {
  const [currentStep, setCurrentStep] = useState<Step | null>(null)

  useEffect(() => {
    const processingStep = steps.find(step => step.status === 'processing')
    setCurrentStep(processingStep || null)
  }, [steps])

  if (!currentStep) return null

  return (
    <div className="flex items-center justify-center space-x-3 mt-4">
      <div className="relative w-6 h-6">
        <div
          className="absolute inset-0 rounded-full animate-spin"
          style={{
            background: 'conic-gradient(from 0deg, #BBE1C3 40%, #DF9B6D , #A6979C  )',
          }}
        />
      </div>
      <span className="font-medium">{currentStep.name}</span>
    </div>
  )
}