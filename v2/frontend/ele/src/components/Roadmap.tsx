import { Progress } from "@/components/ui/progress"

type RoadmapItem = {
  concept: string
  completed: boolean
}

type RoadmapProps = {
  roadmap: RoadmapItem[]
}

export function Roadmap({ roadmap }: RoadmapProps) {
  const completedConcepts = roadmap.filter(item => item.completed).length
  const totalConcepts = roadmap.length
  const progress = (completedConcepts / totalConcepts) * 100

  return (
    <div className="w-full space-y-4">
      <Progress value={progress} className="w-full" />
      <p className="text-sm text-gray-500">
        {completedConcepts} of {totalConcepts} concepts completed
      </p>
      <ul className="space-y-2">
        {roadmap.map((item, index) => (
          <li key={index} className={`flex items-center space-x-2 ${item.completed ? 'text-green-600' : 'text-gray-600'}`}>
            <span>{item.completed ? '✓' : '○'}</span>
            <span>{item.concept}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}