import React, { ChangeEvent } from 'react'
import { Button } from "@/components/ui/button"

type FileUploadProps = {
  file: File | null
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void
  onUpload: () => void
}

export function FileUpload({ file, onFileChange, onUpload }: FileUploadProps) {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative w-full max-w-xs">
      <input
        type="file"
        onChange={onFileChange}
        accept=".pdf"
        className="block w-full max-w-xs text-sm text-gray-500 justify-center
        file:mr-4 file:py-2 file:px-4
        file:rounded-full file:border-0
        file:text-sm file:font-semibold
        file:bg-[#AF1B3F] file:text-white
        hover:file:bg-[#8F1735]
        cursor-pointer"
      />
      {file && (
        <div className="mt-2 text-center">
          <p>Selected file: {file.name}</p>
          <Button onClick={onUpload} className="mt-2 block w-full max-w-xs text-sm text-gray-500 justify-center
        file:mr-4 file:py-2 file:px-4
        file:rounded-full file:border-0
        file:text-sm file:font-semibold
        file:bg-[#AF1B3F] file:text-white
        hover:file:bg-[#AF1B3F]
        cursor-pointer">Upload</Button>
        </div>
      )}
      </div>
    </div>
  )
}