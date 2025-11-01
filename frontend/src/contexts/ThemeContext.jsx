import React, { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Get theme from localStorage or default to 'light'
    const savedTheme = localStorage.getItem('veuplus-theme')
    return savedTheme || 'light'
  })

  const [language, setLanguage] = useState(() => {
    // Get language from localStorage or default to 'ca'
    const savedLanguage = localStorage.getItem('veuplus-language')
    return savedLanguage || 'ca'
  })

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement
    
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    
    // Save to localStorage
    localStorage.setItem('veuplus-theme', theme)
  }, [theme])

  // Save language to localStorage
  useEffect(() => {
    localStorage.setItem('veuplus-language', language)
  }, [language])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  const changeTheme = (newTheme) => {
    setTheme(newTheme)
  }

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage)
  }

  const value = {
    theme,
    language,
    toggleTheme,
    changeTheme,
    changeLanguage,
    isDark: theme === 'dark'
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}
