import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useLesson } from '../hooks/useLesson'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import ReactMarkdown from 'react-markdown'
import { ChatInterface } from '@/components/ChatInterface'

export default function LessonPage() {
  const location = useLocation()
  const { keyConcepts, roadmap: initialRoadmap, initialConcept } = location.state || { keyConcepts: [], roadmap: [], initialConcept: '' }

  const [selectedConcept, setSelectedConcept] = useState(initialConcept)
  const [vocabLevel, setVocabLevel] = useState('mid')
  const { lesson, loading } = useLesson(selectedConcept, vocabLevel)

  useEffect(() => {
    if (!selectedConcept && keyConcepts.length > 0) {
      setSelectedConcept(keyConcepts[0])
    }
  }, [keyConcepts, selectedConcept])

  if (!keyConcepts.length || !initialRoadmap.length) {
    return <div className="min-h-screen flex items-center justify-center">No lesson data available. Please go back and process a PDF first.</div>
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="container mx-auto p-4 flex-grow flex flex-col">
        <h1 className="text-4xl font-bold mb-8 text-[#473144]">Lesson Page</h1>
        
        <div className="flex flex-col md:flex-row gap-6 flex-grow">
          {/* Left Panel: Key Concepts (15% width) */}
          <Card className="bg-white bg-opacity-90 md:w-[15%] min-w-[150px] flex flex-col">
            <CardHeader>
              <CardTitle className="text-[#AF1B3F]">Concepts</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow overflow-hidden">
              <ScrollArea className="h-full">
                {keyConcepts.map((concept, index) => (
                  <Button 
                    key={index}
                    onClick={() => setSelectedConcept(concept)} 
                    className={`w-full mb-2 text-sm rounded-full backdrop-filter backdrop-blur-sm bg-opacity-20 border border-white border-opacity-25 shadow-lg
                      ${selectedConcept === concept 
                        ? 'bg-[#AF1B3F] text-white hover:bg-[#AF1B3F]/90' 
                        : 'bg-[#BBE1C3] text-[#473144] hover:bg-[#BBE1C3]/80'
                      }`}
                    style={{ 
                      whiteSpace: 'normal', 
                      height: 'auto', 
                      padding: '0.75rem 1rem',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {concept}
                  </Button>
                ))}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Middle Panel: Lesson Content (flex-grow) */}
          <Card className="bg-white bg-opacity-90 md:flex-grow flex flex-col overflow-hidden">
            <CardHeader>
              <CardTitle className="text-[#AF1B3F]">Lesson: {selectedConcept}</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow overflow-hidden">
              <ScrollArea className="h-full">
                {loading ? (
                  <p>Loading lesson...</p>
                ) : (
                  <div className="prose max-w-none">
                    <ReactMarkdown>
                      {lesson?.content || 'Select a concept to view the lesson'}
                    </ReactMarkdown>
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Right Panel: Chat (30% width) */}
          <Card className="bg-white bg-opacity-90 md:w-[30%] min-w-[250px] flex flex-col">
            <CardHeader>
              <CardTitle className="text-[#AF1B3F]">Chat</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col">
              <ChatInterface />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}