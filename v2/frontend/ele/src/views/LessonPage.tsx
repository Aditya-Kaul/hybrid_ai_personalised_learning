import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Roadmap } from '../components/Roadmap'
import { KeyConceptsList } from '../components/KeyConceptsList'
import { LessonDisplay } from '../components/LessonDisplay'
import { ChatInterface } from '../components/ChatInterface'
import { Quiz } from '../components/Quiz'
import { useLesson } from '../hooks/useLesson'
import { generateQuiz } from '../services/api'
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type RoadmapItem = {
  concept: string
  completed: boolean
}

export default function LessonPage() {
  const location = useLocation()
  const { keyConcepts, roadmap: initialRoadmap, initialConcept } = location.state || { keyConcepts: [], roadmap: [], initialConcept: '' }

  const [selectedConcept, setSelectedConcept] = useState(initialConcept)
  const [vocabLevel, setVocabLevel] = useState('mid')
  const [showQuiz, setShowQuiz] = useState(false)
  const [quiz, setQuiz] = useState<any>(null)
  const [roadmap, setRoadmap] = useState<RoadmapItem[]>(initialRoadmap)
  const { lesson, loading } = useLesson(selectedConcept, vocabLevel)

  useEffect(() => {
    if (!selectedConcept && keyConcepts.length > 0) {
      setSelectedConcept(keyConcepts[0])
    }
  }, [keyConcepts, selectedConcept])

  const handleConceptClick = (concept: string) => {
    setSelectedConcept(concept)
    setShowQuiz(false)
  }

  const handleCompleteLesson = async () => {
    try {
      const generatedQuiz = await generateQuiz(selectedConcept, 5)
      setQuiz(generatedQuiz)
      setShowQuiz(true)
    } catch (error) {
      console.error('Error generating quiz:', error)
    }
  }

  const handleCompleteQuiz = () => {
    setRoadmap(prevRoadmap => 
      prevRoadmap.map(item => 
        item.concept === selectedConcept ? { ...item, completed: true } : item
      )
    )
    setShowQuiz(false)
  }

  const handleVocabLevelChange = (value: string) => {
    setVocabLevel(value)
  }

  if (!keyConcepts.length || !roadmap.length) {
    return <div className="min-h-screen flex items-center justify-center">No lesson data available. Please go back and process a PDF first.</div>
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <Roadmap roadmap={roadmap} />
      <div className="flex mt-8 space-x-8">
        <KeyConceptsList concepts={keyConcepts} onConceptClick={handleConceptClick} />
        <div className="flex-grow">
          <div className="mb-4">
            <Select onValueChange={handleVocabLevelChange} value={vocabLevel}>
              <SelectTrigger>
                <SelectValue placeholder="Select vocabulary level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="easy">Beginner</SelectItem>
                <SelectItem value="mid">Intermediate</SelectItem>
                <SelectItem value="hard">Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {loading ? (
            <p>Loading lesson...</p>
          ) : showQuiz && quiz ? (
            <Quiz
              questions={quiz.questions}
              onComplete={handleCompleteQuiz}
            />
          ) : (
            <>
              <LessonDisplay lesson={lesson} vocabLevel={vocabLevel} />
              <Button onClick={handleCompleteLesson} className="mt-4">Complete Lesson</Button>
            </>
          )}
        </div>
        <ChatInterface />
      </div>
    </div>
  )
}