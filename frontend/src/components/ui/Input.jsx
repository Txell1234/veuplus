import React from 'react'

const Input = React.forwardRef(
  (
    { className = '', label, helper, id, required, type = 'text', ...props },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).slice(2, 8)}`
    return (
      <div className={`space-y-1 ${className}`}>
        {label ? (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-neutral-700"
          >
            {label}
            {required ? <span className="text-danger-500">*</span> : null}
          </label>
        ) : null}
        <input
          id={inputId}
          ref={ref}
          type={type}
          className="input-field"
          {...props}
        />
        {helper ? (
          <p className="text-xs text-neutral-500 leading-5">{helper}</p>
        ) : null}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
