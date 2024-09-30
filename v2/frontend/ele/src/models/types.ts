export type KeyConcept = string

export type Lesson = {
  content: string
  vocabLevel: 'beginner' | 'intermediate' | 'advanced'
}

export type QuizQuestion = {
  question: string
  options: string[]
  correctAnswer: string
}

export type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}
export type MessageRole = 'user' | 'assistant'

export interface Message {
  role: MessageRole
  content: string
}

export interface ChatResponse {
  response: string
}
