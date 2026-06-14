'use client'

import { useId, useState } from 'react'
import { cn } from '@/lib/utils'

type FloatingInputProps = {
  label: string
  type?: string
  name: string
  required?: boolean
  autoComplete?: string
}

export function FloatingInput({
  label,
  type = 'text',
  name,
  required,
  autoComplete,
}: FloatingInputProps) {
  const id = useId()
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)
  const floated = focused || value.length > 0

  return (
    <div className="relative">
      <input
        id={id}
        name={name}
        type={type}
        required={required}
        autoComplete={autoComplete}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className={cn(
          'peer h-12 w-full rounded-lg border border-border bg-background/60 px-3 pt-4 text-sm text-foreground outline-none transition-shadow',
          'focus:border-primary/60 focus:shadow-glow',
        )}
      />
      <label
        htmlFor={id}
        className={cn(
          'pointer-events-none absolute left-3 text-muted-foreground transition-all duration-200',
          floated ? 'top-1.5 text-[11px] text-primary' : 'top-3.5 text-sm',
        )}
      >
        {label}
      </label>
    </div>
  )
}
