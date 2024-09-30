import { useState, useEffect } from 'react'
import { generateLesson } from '../services/api'

export function useLesson(concept: string, vocabLevel: string) {
  const [lesson, setLesson] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    const fetchLesson = async () => {
      setLoading(true)
      try {
        const lessonContent = await generateLesson(concept, vocabLevel)
        setLesson(lessonContent)
      } catch (error) {
        console.error('Error fetching lesson:', error)
        setLesson('Failed to load lesson. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchLesson()
  }, [concept, vocabLevel])

  return { lesson, loading }
}