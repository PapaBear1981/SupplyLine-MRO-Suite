import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoadingSpinner from './LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />)
    
    // Check if spinner is rendered
    const spinner = screen.getByRole('status')
    expect(spinner).toBeInTheDocument()
    
    // Check if default text is rendered
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders with custom text', () => {
    const customText = 'Please wait...'
    render(<LoadingSpinner text={customText} />)
    
    expect(screen.getByText(customText)).toBeInTheDocument()
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
  })

  it('renders with custom size', () => {
    render(<LoadingSpinner size="lg" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('spinner-lg')
  })

  it('renders without text when text is empty', () => {
    render(<LoadingSpinner text="" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toBeInTheDocument()
    
    // Should not render any text
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
  })

  it('has correct CSS classes', () => {
    render(<LoadingSpinner />)
    
    const container = screen.getByRole('status').parentElement
    expect(container).toHaveClass('d-flex', 'flex-column', 'justify-content-center', 'align-items-center', 'my-5')
  })
})
