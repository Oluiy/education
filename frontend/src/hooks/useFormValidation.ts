// src/hooks/useFormValidation.ts
import { useState, useCallback } from 'react'

interface ValidationRules {
  [key: string]: (value: any) => string | null
}

interface FormErrors {
  [key: string]: string
}

export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationRules: ValidationRules
) {
  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<FormErrors>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const validateField = useCallback((name: string, value: any) => {
    const rule = validationRules[name]
    if (rule) {
      return rule(value)
    }
    return null
  }, [validationRules])

  const validateForm = useCallback(() => {
    const newErrors: FormErrors = {}
    let isValid = true

    Object.keys(validationRules).forEach(field => {
      const error = validateField(field, values[field])
      if (error) {
        newErrors[field] = error
        isValid = false
      }
    })

    setErrors(newErrors)
    return isValid
  }, [values, validateField])

  const handleChange = useCallback((name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }))
    
    if (touched[name]) {
      const error = validateField(name, value)
      setErrors(prev => ({
        ...prev,
        [name]: error || ''
      }))
    }
  }, [touched, validateField])

  const handleBlur = useCallback((name: string) => {
    setTouched(prev => ({ ...prev, [name]: true }))
    
    const error = validateField(name, values[name])
    setErrors(prev => ({
      ...prev,
      [name]: error || ''
    }))
  }, [validateField, values])

  const reset = useCallback(() => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
  }, [initialValues])

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateForm,
    reset,
    setValues
  }
}
