'use client'

import { useState, useRef } from 'react'

const API_BASE_URL = 'http://localhost:8000'

interface AnalysisResults {
  skills: string[]
  organizations: string[]
  categoryAnalysis: Record<string, { score: number; strength: string }>
  topCategories: Array<{ category: string; score: number }>
  recommendedSkills: string[]
}

export default function Home() {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null)
  const [currentStep, setCurrentStep] = useState<'upload' | 'extracting' | 'analyzing' | 'complete'>('upload')
  const [error, setError] = useState<string | null>(null)
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
    setError(null)
    setAnalysisResults(null)
    setCurrentStep('upload')

    try {
      // Step 1: Upload resume and extract text
      setCurrentStep('extracting')
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await fetch(`${API_BASE_URL}/upload-resume`, {
        method: 'POST',
        body: formData,
      })

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json()
        throw new Error(errorData.detail || 'Failed to upload resume')
      }

      const uploadData = await uploadResponse.json()
      const extractedText = uploadData.text

      // Step 2: Extract skills using NER
      const extractResponse = await fetch(`${API_BASE_URL}/extract-skills`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: extractedText }),
      })

      if (!extractResponse.ok) {
        const errorData = await extractResponse.json()
        throw new Error(errorData.detail || 'Failed to extract skills')
      }

      const extractData = await extractResponse.json()
      const skills = extractData.skills

      // Step 3: Analyze skills using sentence transformers
      setCurrentStep('analyzing')
      const analyzeResponse = await fetch(`${API_BASE_URL}/analyze-skills`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ skills }),
      })

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json()
        throw new Error(errorData.detail || 'Failed to analyze skills')
      }

      const analyzeData = await analyzeResponse.json()

      // Combine results
      setAnalysisResults({
        skills: extractData.skills,
        organizations: extractData.organizations,
        categoryAnalysis: analyzeData.category_analysis,
        topCategories: analyzeData.top_categories,
        recommendedSkills: analyzeData.recommended_skills,
      })

      setIsUploading(false)
      setUploadSuccess(true)
      setCurrentStep('complete')
    } catch (err) {
      setIsUploading(false)
      setError(err instanceof Error ? err.message : 'An error occurred')
      setCurrentStep('upload')
    }
  }

  const handleRemoveFile = () => {
    setUploadedFile(null)
    setUploadSuccess(false)
    setAnalysisResults(null)
    setError(null)
    setCurrentStep('upload')
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
                    <p className="text-gray-600 font-medium mb-2">
                      {currentStep === 'extracting' && 'Extracting text from resume...'}
                      {currentStep === 'analyzing' && 'Analyzing skills with AI...'}
                      {currentStep === 'upload' && 'Uploading your resume...'}
                    </p>
                    <p className="text-sm text-gray-500">
                      This may take a few moments
                    </p>
                  </div>
                ) : error ? (
                  <div className="py-8">
                    <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                      <svg
                        className="w-10 h-10 text-red-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-red-700 mb-2">
                      Error
                    </h3>
                    <p className="text-gray-600 mb-6 text-sm">
                      {error}
                    </p>
                    <button
                      onClick={handleRemoveFile}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                    >
                      Try Again
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

        {/* Analysis Results */}
        {analysisResults && (
          <div className="mt-8 animate-slide-up space-y-6">
            {/* Skills Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Extracted Skills
              </h2>
              <div className="flex flex-wrap gap-2">
                {analysisResults.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Top Categories */}
            {analysisResults.topCategories.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                  <svg className="w-6 h-6 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Top Skill Categories
                </h2>
                <div className="space-y-3">
                  {analysisResults.topCategories.map((category, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="font-medium text-gray-800">{category.category}</span>
                      <div className="flex items-center">
                        <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${category.score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold text-gray-600 w-12 text-right">
                          {(category.score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Category Analysis */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Category Analysis
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(analysisResults.categoryAnalysis).map(([category, data]) => (
                  <div key={category} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-800">{category}</span>
                      <span className={`text-sm font-semibold px-2 py-1 rounded ${
                        data.strength === 'Strong' ? 'bg-green-100 text-green-700' :
                        data.strength === 'Moderate' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {data.strength}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          data.strength === 'Strong' ? 'bg-green-500' :
                          data.strength === 'Moderate' ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${data.score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

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

