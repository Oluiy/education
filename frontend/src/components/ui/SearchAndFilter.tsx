'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'

interface FilterOption {
  label: string
  value: string
  count?: number
}

interface FilterConfig {
  id: string
  label: string
  type: 'select' | 'multiselect' | 'range' | 'date'
  options?: FilterOption[]
  min?: number
  max?: number
}

interface SearchAndFilterProps {
  searchPlaceholder?: string
  searchValue: string
  onSearchChange: (value: string) => void
  filters?: FilterConfig[]
  activeFilters: Record<string, any>
  onFilterChange: (filterId: string, value: any) => void
  onClearFilters: () => void
  sortOptions?: FilterOption[]
  sortValue?: string
  onSortChange?: (value: string) => void
  resultsCount?: number
  className?: string
}

export function SearchAndFilter({
  searchPlaceholder = "Search...",
  searchValue,
  onSearchChange,
  filters = [],
  activeFilters,
  onFilterChange,
  onClearFilters,
  sortOptions,
  sortValue,
  onSortChange,
  resultsCount,
  className = ""
}: SearchAndFilterProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [showSort, setShowSort] = useState(false)

  const activeFilterCount = useMemo(() => {
    return Object.values(activeFilters).filter(value => {
      if (Array.isArray(value)) return value.length > 0
      return value !== null && value !== undefined && value !== ''
    }).length
  }, [activeFilters])

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search and Controls Row */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Search Bar */}
        <div className="relative flex-1 max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {/* Filter Button */}
          {filters.length > 0 && (
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`relative flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${
                showFilters || activeFilterCount > 0
                  ? 'bg-primary-50 border-primary-200 text-primary-700'
                  : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FunnelIcon className="w-4 h-4" />
              <span>Filters</span>
              {activeFilterCount > 0 && (
                <span className="absolute -top-2 -right-2 w-5 h-5 bg-primary-600 text-white text-xs rounded-full flex items-center justify-center">
                  {activeFilterCount}
                </span>
              )}
            </button>
          )}

          {/* Sort Dropdown */}
          {sortOptions && sortOptions.length > 0 && (
            <div className="relative">
              <button
                onClick={() => setShowSort(!showSort)}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <span>Sort</span>
                <ChevronDownIcon className="w-4 h-4" />
              </button>
              
              <AnimatePresence>
                {showSort && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
                  >
                    <div className="py-2">
                      {sortOptions.map(option => (
                        <button
                          key={option.value}
                          onClick={() => {
                            onSortChange?.(option.value)
                            setShowSort(false)
                          }}
                          className={`w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors ${
                            sortValue === option.value ? 'bg-primary-50 text-primary-700' : ''
                          }`}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Results Count */}
          {resultsCount !== undefined && (
            <span className="text-sm text-gray-600">
              {resultsCount} result{resultsCount !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Active Filters Display */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-gray-600">Active filters:</span>
          {Object.entries(activeFilters).map(([filterId, value]) => {
            if (!value || (Array.isArray(value) && value.length === 0)) return null
            
            const filter = filters.find(f => f.id === filterId)
            if (!filter) return null

            const displayValue = Array.isArray(value) 
              ? value.length > 1 ? `${value.length} selected` : value[0]
              : value

            return (
              <motion.div
                key={filterId}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
              >
                <span>{filter.label}: {displayValue}</span>
                <button
                  onClick={() => onFilterChange(filterId, Array.isArray(value) ? [] : '')}
                  className="hover:bg-primary-200 rounded-full p-0.5"
                >
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </motion.div>
            )
          })}
          <button
            onClick={onClearFilters}
            className="text-sm text-primary-600 hover:text-primary-500 underline"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gray-50 border border-gray-200 rounded-lg p-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filters.map(filter => (
                <FilterControl
                  key={filter.id}
                  filter={filter}
                  value={activeFilters[filter.id]}
                  onChange={(value) => onFilterChange(filter.id, value)}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

interface FilterControlProps {
  filter: FilterConfig
  value: any
  onChange: (value: any) => void
}

function FilterControl({ filter, value, onChange }: FilterControlProps) {
  switch (filter.type) {
    case 'select':
      return (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {filter.label}
          </label>
          <select
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All</option>
            {filter.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label} {option.count && `(${option.count})`}
              </option>
            ))}
          </select>
        </div>
      )

    case 'multiselect':
      return (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {filter.label}
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {filter.options?.map(option => (
              <label key={option.value} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={Array.isArray(value) && value.includes(option.value)}
                  onChange={(e) => {
                    const currentValues = Array.isArray(value) ? value : []
                    if (e.target.checked) {
                      onChange([...currentValues, option.value])
                    } else {
                      onChange(currentValues.filter(v => v !== option.value))
                    }
                  }}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">
                  {option.label} {option.count && `(${option.count})`}
                </span>
              </label>
            ))}
          </div>
        </div>
      )

    case 'range':
      return (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {filter.label}
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              placeholder="Min"
              min={filter.min}
              max={filter.max}
              value={value?.min || ''}
              onChange={(e) => onChange({ ...value, min: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <span className="text-gray-500">to</span>
            <input
              type="number"
              placeholder="Max"
              min={filter.min}
              max={filter.max}
              value={value?.max || ''}
              onChange={(e) => onChange({ ...value, max: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      )

    case 'date':
      return (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {filter.label}
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="date"
              value={value?.from || ''}
              onChange={(e) => onChange({ ...value, from: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={value?.to || ''}
              onChange={(e) => onChange({ ...value, to: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      )

    default:
      return null
  }
}
