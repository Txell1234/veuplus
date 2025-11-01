import React from 'react'

const Card = ({ className = '', children, as: Component = 'div', ...props }) => (
  <Component
    className={`card border border-neutral-100 bg-white shadow-sm shadow-primary-900/5 ${className}`}
    {...props}
  >
    {children}
  </Component>
)

export default Card
