import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"

type KeyConceptsListProps = {
  concepts: string[]
  onConceptClick: (concept: string) => void
}

export function KeyConceptsList({ concepts, onConceptClick }: KeyConceptsListProps) {
  return (
    <ScrollArea className="h-[400px] w-[200px] rounded-md border p-4">
      {concepts.map((concept, index) => (
        <Button
          key={index}
          variant="ghost"
          className="w-full justify-start"
          onClick={() => onConceptClick(concept)}
        >
          {concept}
        </Button>
      ))}
    </ScrollArea>
  )
}