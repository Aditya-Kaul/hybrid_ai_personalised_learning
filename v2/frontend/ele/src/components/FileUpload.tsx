import React, { ChangeEvent } from 'react'
import { Button } from "@/components/ui/button"

type FileUploadProps = {
  file: File | null
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void
  onUpload: () => void
}

export function FileUpload({ file, onFileChange, onUpload }: FileUploadProps) {
  return (
    <div className="space-y-4">
      <input
        type="file"
        onChange={onFileChange}
        accept=".pdf"
        className="block w-full text-sm text-gray-500
          file:mr-4 file:py-2 file:px-4
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-violet-50 file:text-violet-700
          hover:file:bg-violet-100"
      />
      {file && (
        <div className="mt-2">
          <p>Selected file: {file.name}</p>
          <Button onClick={onUpload} className="mt-2">Upload</Button>
        </div>
      )}
    </div>
  )
}