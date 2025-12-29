'use client'

import { useState, useRef } from 'react'

export default function Home() {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileSelect = (file: File) => {
    // Validate file type
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!validTypes.includes(file.type)) {
      alert('Please upload a PDF or Word document (.pdf, .doc, .docx)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }

    setUploadedFile(file)
    handleUpload(file)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleUpload = async (file: File) => {
    setIsUploading(true)
    setUploadSuccess(false)

    // Simulate upload process
    await new Promise(resolve => setTimeout(resolve, 1500))

    setIsUploading(false)
    setUploadSuccess(true)

    // Reset success message after 3 seconds
    setTimeout(() => {
      setUploadSuccess(false)
    }, 3000)
  }

  const handleRemoveFile = () => {
    setUploadedFile(null)
    setUploadSuccess(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header Section */}
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4 animate-slide-up">
            Find Your Path
          </h1>
          <p className="text-xl text-gray-600 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Upload your resume to discover your career journey
          </p>
        </div>

        {/* Upload Section */}
        <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <div
            className={`
              relative border-2 border-dashed rounded-2xl p-12
              transition-all duration-300 ease-in-out
              ${isDragging 
                ? 'border-blue-500 bg-blue-50 scale-105 shadow-xl' 
                : 'border-gray-300 bg-white hover:border-blue-400 hover:shadow-lg'
              }
              ${uploadSuccess ? 'border-green-500 bg-green-50' : ''}
            `}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {!uploadedFile ? (
              <div className="text-center">
                <div className="mb-6 flex justify-center">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center transform transition-transform duration-300 hover:scale-110">
                    <svg
                      className="w-10 h-10 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                  </div>
                </div>
                <h3 className="text-2xl font-semibold text-gray-800 mb-2">
                  Drop your resume here
                </h3>
                <p className="text-gray-500 mb-6">
                  or click to browse
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg shadow-md hover:shadow-xl transform transition-all duration-300 hover:scale-105 hover:from-blue-700 hover:to-indigo-700"
                >
                  Select File
                </button>
                <p className="text-sm text-gray-400 mt-4">
                  Supports PDF, DOC, DOCX (Max 10MB)
                </p>
              </div>
            ) : (
              <div className="text-center">
                {isUploading ? (
                  <div className="py-8">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mb-4"></div>
                    <p className="text-gray-600 font-medium">Uploading your resume...</p>
                  </div>
                ) : uploadSuccess ? (
                  <div className="py-8">
                    <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mx-auto mb-4 animate-pulse-slow">
                      <svg
                        className="w-10 h-10 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                    <h3 className="text-2xl font-semibold text-green-700 mb-2">
                      Upload Successful!
                    </h3>
                    <p className="text-gray-600 mb-6">
                      Your resume has been uploaded successfully
                    </p>
                    <button
                      onClick={handleRemoveFile}
                      className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors duration-200"
                    >
                      Upload Another
                    </button>
                  </div>
                ) : (
                  <div className="py-4">
                    <div className="flex items-center justify-center mb-4">
                      <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                        <svg
                          className="w-6 h-6 text-blue-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </div>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">
                      {uploadedFile.name}
                    </h3>
                    <p className="text-sm text-gray-500 mb-6">
                      {formatFileSize(uploadedFile.size)}
                    </p>
                    <button
                      onClick={handleRemoveFile}
                      className="px-6 py-2 text-red-600 hover:text-red-700 font-medium transition-colors duration-200"
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileInputChange}
              className="hidden"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <p className="text-sm text-gray-500">
            Secure and confidential • Your data is protected
          </p>
        </div>
      </div>
    </main>
  )
}

