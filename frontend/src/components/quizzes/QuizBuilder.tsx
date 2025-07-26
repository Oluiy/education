// src/components/quizzes/QuizBuilder.tsx
'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Quiz, Question } from '../../api/quizzes'
import { useApi } from '../../hooks/useApi'
import { useToast } from '../../contexts/ToastContext'
import {
  PlusIcon,
  TrashIcon,
  EyeIcon,
  BookmarkIcon,
  RocketLaunchIcon,
  ArrowLeftIcon,
  QuestionMarkCircleIcon,
  Bars3Icon
} from '@heroicons/react/24/outline'

const questionSchema = z.object({
  question: z.string().min(1, 'Question is required'),
  type: z.enum(['multiple-choice', 'true-false', 'short-answer', 'essay']),
  options: z.array(z.string()).optional(),
  correctAnswer: z.string().min(1, 'Correct answer is required'),
  points: z.number().min(1, 'Points must be at least 1'),
  explanation: z.string().optional()
})

const quizSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  courseId: z.string().optional(),
  timeLimit: z.number().optional(),
  attempts: z.number().min(1, 'At least 1 attempt required'),
  passingScore: z.number().min(0).max(100, 'Passing score must be 0-100'),
  randomizeQuestions: z.boolean(),
  showResults: z.boolean(),
  questions: z.array(questionSchema).min(1, 'At least 1 question required')
})

type QuizFormData = z.infer<typeof quizSchema>

interface QuizBuilderProps {
  quiz?: Quiz
  courseId?: string
  onSave?: () => void
  onCancel?: () => void
}

export function QuizBuilder({ quiz, courseId, onSave, onCancel }: QuizBuilderProps) {
  const [previewMode, setPreviewMode] = useState(false)
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  
  const { createQuiz, updateQuiz, publishQuiz } = useApi()
  const { success, error } = useToast()

  const form = useForm<QuizFormData>({
    resolver: zodResolver(quizSchema),
    defaultValues: quiz ? {
      title: quiz.title,
      description: quiz.description,
      courseId: quiz.courseId || courseId,
      timeLimit: quiz.timeLimit,
      attempts: quiz.attempts,
      passingScore: quiz.passingScore,
      randomizeQuestions: quiz.randomizeQuestions,
      showResults: quiz.showResults,
      questions: quiz.questions.map(q => ({
        question: q.question,
        type: q.type,
        correctAnswer: Array.isArray(q.correctAnswer) ? q.correctAnswer.join(',') : q.correctAnswer,
        points: q.points,
        options: q.options,
        explanation: q.explanation
      }))
    } : {
      title: '',
      description: '',
      courseId: courseId || '',
      timeLimit: undefined,
      attempts: 3,
      passingScore: 70,
      randomizeQuestions: false,
      showResults: true,
      questions: []
    }
  })

  const { fields, append, remove, move } = useFieldArray({
    control: form.control,
    name: 'questions'
  })

  const addQuestion = () => {
    append({
      question: '',
      type: 'multiple-choice',
      options: ['', '', '', ''],
      correctAnswer: '',
      points: 1,
      explanation: ''
    })
  }

  const handleSave = async (data: QuizFormData, publish = false) => {
    try {
      let savedQuiz: Quiz

      if (quiz?.id) {
        savedQuiz = await updateQuiz.mutateAsync({
          id: quiz.id,
          data: { 
            ...data, 
            isPublished: publish,
            questions: data.questions.map((q, index) => ({
              ...q,
              id: quiz.questions[index]?.id || `temp-${Date.now()}-${index}`,
              order: index,
              correctAnswer: q.type === 'multiple-choice' && q.options ? 
                q.correctAnswer : q.correctAnswer
            }))
          }
        })
      } else {
        savedQuiz = await createQuiz.mutateAsync({
          ...data,
          isPublished: publish,
          questions: data.questions.map((q, index) => ({
            ...q,
            id: `temp-${Date.now()}-${index}`,
            order: index,
            correctAnswer: q.type === 'multiple-choice' && q.options ? 
              q.correctAnswer : q.correctAnswer
          }))
        })
      }

      if (publish && !quiz?.isPublished) {
        await publishQuiz.mutateAsync(savedQuiz.id)
      }

      success(
        `Quiz ${quiz ? 'updated' : 'created'}${publish ? ' and published' : ''} successfully`
      )
      onSave?.()
    } catch (err) {
      error(
        `Failed to ${quiz ? 'update' : 'create'} quiz: ${err instanceof Error ? err.message : 'Unknown error'}`
      )
    }
  }

  const handleDragStart = (index: number) => {
    setDraggedIndex(index)
  }

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggedIndex !== null && draggedIndex !== index) {
      move(draggedIndex, index)
      setDraggedIndex(index)
    }
  }

  const handleDragEnd = () => {
    setDraggedIndex(null)
  }

  if (previewMode) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setPreviewMode(false)}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span>Back to Edit</span>
            </button>
            <span className="text-sm text-gray-500">Preview Mode</span>
          </div>

          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{form.watch('title')}</h1>
            <p className="text-gray-600 mb-6">{form.watch('description')}</p>
            
            <div className="flex items-center space-x-6 text-sm text-gray-500 mb-6">
              <span>{fields.length} questions</span>
              {form.watch('timeLimit') && <span>{form.watch('timeLimit')} minutes</span>}
              <span>{form.watch('passingScore')}% to pass</span>
              <span>{form.watch('attempts')} attempts</span>
            </div>
          </div>

          <div className="space-y-6">
            {fields.map((field, index) => (
              <div key={field.id} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Question {index + 1} ({form.watch(`questions.${index}.points`)} points)
                  </h3>
                  <span className="text-sm text-gray-500 capitalize">
                    {form.watch(`questions.${index}.type`).replace('-', ' ')}
                  </span>
                </div>
                
                <p className="text-gray-700 mb-4">{form.watch(`questions.${index}.question`)}</p>
                
                {form.watch(`questions.${index}.type`) === 'multiple-choice' && (
                  <div className="space-y-2">
                    {form.watch(`questions.${index}.options`)?.map((option, optIndex) => (
                      option && (
                        <div 
                          key={optIndex} 
                          className={`p-3 rounded-lg border ${
                            option === form.watch(`questions.${index}.correctAnswer`)
                              ? 'border-green-500 bg-green-50'
                              : 'border-gray-200'
                          }`}
                        >
                          {option}
                        </div>
                      )
                    ))}
                  </div>
                )}

                {form.watch(`questions.${index}.type`) === 'true-false' && (
                  <div className="space-y-2">
                    <div className={`p-3 rounded-lg border ${
                      form.watch(`questions.${index}.correctAnswer`) === 'true'
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200'
                    }`}>
                      True
                    </div>
                    <div className={`p-3 rounded-lg border ${
                      form.watch(`questions.${index}.correctAnswer`) === 'false'
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200'
                    }`}>
                      False
                    </div>
                  </div>
                )}

                {form.watch(`questions.${index}.explanation`) && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-800">
                      <strong>Explanation:</strong> {form.watch(`questions.${index}.explanation`)}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={form.handleSubmit((data: QuizFormData) => handleSave(data))} className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {quiz ? 'Edit Quiz' : 'Create Quiz'}
            </h1>
            <p className="text-gray-600 mt-2">
              Build engaging quizzes for your students
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={() => setPreviewMode(true)}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <EyeIcon className="w-4 h-4" />
              <span>Preview</span>
            </button>
            
            <button
              type="submit"
              disabled={createQuiz.isPending || updateQuiz.isPending}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <BookmarkIcon className="w-4 h-4" />
              <span>{createQuiz.isPending || updateQuiz.isPending ? 'Saving...' : 'Save Draft'}</span>
            </button>
            
            <button
              type="button"
              onClick={() => form.handleSubmit((data: QuizFormData) => handleSave(data, true))()}
              disabled={createQuiz.isPending || updateQuiz.isPending || publishQuiz.isPending}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <RocketLaunchIcon className="w-4 h-4" />
              <span>
                {publishQuiz.isPending ? 'Publishing...' : quiz?.isPublished ? 'Update & Publish' : 'Save & Publish'}
              </span>
            </button>
          </div>
        </div>

        {/* Quiz Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quiz Title *
            </label>
            <input
              {...form.register('title')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter quiz title"
            />
            {form.formState.errors.title && (
              <p className="text-red-500 text-sm mt-1">{form.formState.errors.title.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Limit (minutes)
            </label>
            <input
              type="number"
              {...form.register('timeLimit', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="No limit"
            />
          </div>

          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              {...form.register('description')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describe what this quiz covers"
            />
            {form.formState.errors.description && (
              <p className="text-red-500 text-sm mt-1">{form.formState.errors.description.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attempts Allowed *
            </label>
            <input
              type="number"
              min="1"
              {...form.register('attempts', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Passing Score (%) *
            </label>
            <input
              type="number"
              min="0"
              max="100"
              {...form.register('passingScore', { valueAsNumber: true })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="lg:col-span-2">
            <div className="flex items-center space-x-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...form.register('randomizeQuestions')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Randomize question order</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  {...form.register('showResults')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Show results after submission</span>
              </label>
            </div>
          </div>
        </div>

        {/* Questions */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Questions</h2>
            <button
              type="button"
              onClick={addQuestion}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <PlusIcon className="w-4 h-4" />
              <span>Add Question</span>
            </button>
          </div>

          <AnimatePresence>
            {fields.map((field, index) => (
              <QuestionEditor
                key={field.id}
                index={index}
                form={form}
                onRemove={() => remove(index)}
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
                isDragging={draggedIndex === index}
              />
            ))}
          </AnimatePresence>

          {fields.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <QuestionMarkCircleIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No questions yet. Add your first question to get started.</p>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-between pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-500">
              {fields.length} question{fields.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </div>
    </form>
  )
}

// Question Editor Component
interface QuestionEditorProps {
  index: number
  form: any
  onRemove: () => void
  onDragStart: () => void
  onDragOver: (e: React.DragEvent) => void
  onDragEnd: () => void
  isDragging: boolean
}

function QuestionEditor({ 
  index, 
  form, 
  onRemove, 
  onDragStart, 
  onDragOver, 
  onDragEnd, 
  isDragging 
}: QuestionEditorProps) {
  const questionType = form.watch(`questions.${index}.type`)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`mb-6 border border-gray-200 rounded-lg p-6 ${isDragging ? 'opacity-50' : ''}`}
      draggable
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragEnd={onDragEnd}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="cursor-move">
            <Bars3Icon className="w-5 h-5 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900">Question {index + 1}</h3>
        </div>
        
        <button
          type="button"
          onClick={onRemove}
          className="text-red-600 hover:text-red-700"
        >
          <TrashIcon className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Question Type
          </label>
          <select
            {...form.register(`questions.${index}.type`)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="multiple-choice">Multiple Choice</option>
            <option value="true-false">True/False</option>
            <option value="short-answer">Short Answer</option>
            <option value="essay">Essay</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Points
          </label>
          <input
            type="number"
            min="1"
            {...form.register(`questions.${index}.points`, { valueAsNumber: true })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Question *
        </label>
        <textarea
          {...form.register(`questions.${index}.question`)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter your question"
        />
      </div>

      {/* Multiple Choice Options */}
      {questionType === 'multiple-choice' && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Answer Options
          </label>
          <div className="space-y-2">
            {[0, 1, 2, 3].map((optIndex) => (
              <div key={optIndex} className="flex items-center space-x-3">
                <input
                  type="radio"
                  {...form.register(`questions.${index}.correctAnswer`)}
                  value={form.watch(`questions.${index}.options.${optIndex}`) || ''}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <input
                  {...form.register(`questions.${index}.options.${optIndex}`)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={`Option ${optIndex + 1}`}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* True/False Options */}
      {questionType === 'true-false' && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Correct Answer
          </label>
          <div className="flex items-center space-x-6">
            <label className="flex items-center">
              <input
                type="radio"
                {...form.register(`questions.${index}.correctAnswer`)}
                value="true"
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">True</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                {...form.register(`questions.${index}.correctAnswer`)}
                value="false"
                className="text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2">False</span>
            </label>
          </div>
        </div>
      )}

      {/* Short Answer/Essay Correct Answer */}
      {(questionType === 'short-answer' || questionType === 'essay') && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {questionType === 'essay' ? 'Sample Answer/Rubric' : 'Correct Answer'}
          </label>
          <textarea
            {...form.register(`questions.${index}.correctAnswer`)}
            rows={questionType === 'essay' ? 4 : 2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={questionType === 'essay' ? 'Provide a sample answer or grading rubric' : 'Enter the correct answer'}
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Explanation (Optional)
        </label>
        <textarea
          {...form.register(`questions.${index}.explanation`)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Explain why this is the correct answer"
        />
      </div>
    </motion.div>
  )
}
