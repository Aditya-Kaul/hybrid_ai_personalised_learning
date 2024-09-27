import { Message, ChatResponse } from '../models/types'

const API_BASE_URL = 'http://localhost:8000'

export async function uploadPDF(file: File): Promise<string[]> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('PDF upload failed')
  }

  const data = await response.json()
  return data.key_concepts
}

export async function testUploadPDF(file: File): Promise<any> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/test-upload-pdf`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error('Test PDF upload failed')
  }

  return response.json()
}

export function generateClientSideRoadmap(keyConcepts: string[]): { concept: string; completed: boolean }[] {
  return keyConcepts.map(concept => ({
    concept,
    completed: false
  }))
}

export async function generateLesson(concept: string, vocabulary: string = 'mid'): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/generate-lesson/${concept}?vocabulary=${vocabulary}`)

  if (!response.ok) {
    throw new Error('Failed to generate lesson')
  }

  const data = await response.json()
  return data.lesson
}

export async function generateQuiz(concept: string, numQuestions: number = 5): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/generate-quiz/${concept}?num_questions=${numQuestions}`)

  if (!response.ok) {
    throw new Error('Failed to generate quiz')
  }

  return response.json()
}

export async function chat(query: string, chatHistory: any[]): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, chat_history: chatHistory }),
  })

  if (!response.ok) {
    throw new Error('Chat request failed')
  }

  const data = await response.json()
  return data.response
}

export async function getRootMessage(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/`)

  if (!response.ok) {
    throw new Error('Failed to get root message')
  }

  const data = await response.json()
  return data.message
}

// Example usage of uploadPDF and generateRoadmap
export async function processAndGenerateRoadmap(file: File): Promise<{ concept: string; completed: boolean }[]> {
  try {
    const keyConcepts = await uploadPDF(file)
    return generateClientSideRoadmap(keyConcepts)
  } catch (error) {
    console.error('Error processing PDF and generating roadmap:', error)
    throw error
  }
}

export async function streamChat(
  query: string, 
  chatHistory: Message[], 
  onChunk: (chunk: string) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, chat_history: chatHistory }),
  })

  if (!response.ok) {
    throw new Error('Chat request failed')
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('Failed to get response reader')
  }

  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    
    // Try to parse complete JSON objects from the buffer
    let startIndex = 0
    while (true) {
      const endIndex = buffer.indexOf('}', startIndex)
      if (endIndex === -1) break
      
      try {
        const json = JSON.parse(buffer.slice(startIndex, endIndex + 1)) as ChatResponse
        if (json.response) {
          onChunk(json.response)
        }
        startIndex = endIndex + 1
      } catch (e) {
        // If parsing fails, we don't have a complete JSON object yet
        break
      }
    }
    
    // Remove processed data from the buffer
    buffer = buffer.slice(startIndex)
  }
  
  // Process any remaining data in the buffer
  if (buffer) {
    try {
      const json = JSON.parse(buffer) as ChatResponse
      if (json.response) {
        onChunk(json.response)
      }
    } catch (e) {
      console.error('Error parsing final chunk:', e)
    }
  }
}