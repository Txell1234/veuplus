import React from 'react'

const colorClasses = {
  default: 'bg-neutral-100 text-neutral-700',
  primary: 'bg-primary-100 text-primary-700',
  accent: 'bg-accent-100 text-accent-700',
  success: 'bg-success-100 text-success-700',
  warning: 'bg-warning-100 text-warning-700',
  danger: 'bg-danger-100 text-danger-700',
}

const Badge = ({ variant = 'default', className = '', children }) => {
  const tone = colorClasses[variant] || colorClasses.default
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${tone} ${className}`}
    >
      {children}
    </span>
  )
}

export default Badge
