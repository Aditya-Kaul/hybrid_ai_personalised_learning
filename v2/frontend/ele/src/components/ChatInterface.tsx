import React, { useState, useRef, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { streamChat } from "../services/api"
import { Message } from "../models/types"

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (input.trim() && !isLoading) {
      const userMessage: Message = { role: 'user', content: input.trim() }
      setMessages(prevMessages => [...prevMessages, userMessage])
      setInput("")
      setIsLoading(true)

      try {
        const assistantMessage: Message = { role: 'assistant', content: '' }
        setMessages(prevMessages => [...prevMessages, assistantMessage])

        await streamChat(
          input.trim(),
          messages,
          (chunk: string) => {
            setMessages(prevMessages => {
              const updatedMessages = [...prevMessages]
              const lastMessage = updatedMessages[updatedMessages.length - 1]
              if (lastMessage.role === 'assistant') {
                lastMessage.content += chunk
              }
              return updatedMessages
            })
          }
        )
      } catch (error) {
        console.error('Error in chat:', error)
        setMessages(prevMessages => [
          ...prevMessages,
          { role: 'assistant', content: 'Sorry, an error occurred. Please try again.' }
        ])
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="flex flex-col h-[400px] w-[300px] border rounded-lg p-4">
      <ScrollArea className="flex-grow mb-4" ref={scrollAreaRef}>
        {messages.map((message, index) => (
          <div key={index} className={`p-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block p-2 rounded-lg ${
              message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'
            }`}>
              {message.content}
            </span>
          </div>
        ))}
      </ScrollArea>
      <div className="flex mt-4">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-grow"
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={isLoading}
        />
        <Button onClick={handleSend} className="ml-2" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </Button>
      </div>
    </div>
  )
}