import { CheckCircle, Circle } from "lucide-react"

type Step = {
  name: string
  status: 'pending' | 'completed'
}

type ProcessingStepsProps = {
  steps: Step[]
}

export function ProcessingSteps({ steps }: ProcessingStepsProps) {
  return (
    <div className="space-y-2">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center space-x-2">
          {step.status === 'completed' ? (
            <CheckCircle className="text-green-500" />
          ) : (
            <Circle className="text-gray-300" />
          )}
          <span>{step.name}</span>
        </div>
      ))}
    </div>
  )
}