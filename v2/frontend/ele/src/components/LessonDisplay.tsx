import { Card, CardContent } from "@/components/ui/card"
import ReactMarkdown from 'react-markdown'

type LessonDisplayProps = {
  lesson: string
  vocabLevel: string
}

export function LessonDisplay({ lesson, vocabLevel }: LessonDisplayProps) {
  return (
    <Card className="w-[600px]">
      <CardContent>
        <ReactMarkdown>{lesson}</ReactMarkdown>
        <p className="text-sm text-gray-500 mt-4">Vocabulary Level: {vocabLevel}</p>
      </CardContent>
    </Card>
  )
}