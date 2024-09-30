import { useState } from "react"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

type Question = {
  question: string
  options: string[]
  correctAnswer: string
}

type QuizProps = {
  questions: Question[]
  onComplete: () => void
}

export function Quiz({ questions, onComplete }: QuizProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState("")
  const [score, setScore] = useState(0)

  const handleSubmit = () => {
    if (selectedAnswer === questions[currentQuestion].correctAnswer) {
      setScore(score + 1)
    }

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setSelectedAnswer("")
    } else {
      onComplete()
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">{questions[currentQuestion].question}</h2>
      <RadioGroup value={selectedAnswer} onValueChange={setSelectedAnswer}>
        {questions[currentQuestion].options.map((option, index) => (
          <div key={index} className="flex items-center space-x-2">
            <RadioGroupItem value={option} id={`option-${index}`} />
            <Label htmlFor={`option-${index}`}>{option}</Label>
          </div>
        ))}
      </RadioGroup>
      <Button onClick={handleSubmit} disabled={!selectedAnswer}>
        {currentQuestion < questions.length - 1 ? "Next" : "Finish"}
      </Button>
      <p>Score: {score} / {currentQuestion + 1}</p>
    </div>
  )
}