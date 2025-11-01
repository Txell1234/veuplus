import React from 'react'

const baseClasses =
  'inline-flex items-center justify-center rounded-xl font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white disabled:opacity-50 disabled:cursor-not-allowed gap-2'

const variants = {
  primary:
    'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-400 shadow-sm',
  secondary:
    'bg-white text-neutral-700 border border-neutral-200 hover:bg-primary-50 focus:ring-primary-200',
  ghost:
    'bg-transparent text-neutral-600 hover:bg-neutral-100 focus:ring-neutral-200',
  danger:
    'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-400 shadow-sm',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base',
}

const Button = React.forwardRef(
  (
    {
      as: Component = 'button',
      variant = 'primary',
      size = 'md',
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    const variantClasses = variants[variant] || variants.primary
    const sizeClasses = sizes[size] || sizes.md
    return (
      <Component
        ref={ref}
        className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
        {...props}
      >
        {children}
      </Component>
    )
  }
)

Button.displayName = 'Button'

export default Button
