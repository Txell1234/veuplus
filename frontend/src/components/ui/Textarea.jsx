import React from 'react'

const Textarea = React.forwardRef(
  ({ className = '', label, helper, id, required, rows = 4, ...props }, ref) => {
    const textareaId =
      id || `textarea-${Math.random().toString(36).slice(2, 8)}`
    return (
      <div className={`space-y-1 ${className}`}>
        {label ? (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-neutral-700"
          >
            {label}
            {required ? <span className="text-danger-500">*</span> : null}
          </label>
        ) : null}
        <textarea
          id={textareaId}
          ref={ref}
          rows={rows}
          className="input-field min-h-[120px]"
          {...props}
        />
        {helper ? (
          <p className="text-xs text-neutral-500 leading-5">{helper}</p>
        ) : null}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

export default Textarea
