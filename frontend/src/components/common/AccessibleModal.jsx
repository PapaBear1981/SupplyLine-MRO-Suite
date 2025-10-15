import React, { useEffect, useRef, useCallback } from 'react';
import { Modal } from 'react-bootstrap';
import PropTypes from 'prop-types';

/**
 * AccessibleModal - A WCAG 2.1 AA compliant modal wrapper
 * 
 * Features:
 * - Focus trap: Keeps focus within modal when open
 * - Keyboard navigation: ESC to close, Tab cycles through focusable elements
 * - Auto-focus: Focuses first focusable element on open
 * - Focus restoration: Returns focus to trigger element on close
 * - ARIA attributes: Proper labeling and roles
 * 
 * WCAG Compliance:
 * - 2.1.2 No Keyboard Trap (Level A)
 * - 2.4.3 Focus Order (Level A)
 * - 3.2.1 On Focus (Level A)
 */
const AccessibleModal = ({
  show,
  onHide,
  title,
  children,
  footer,
  size = 'md',
  centered = true,
  backdrop = true,
  keyboard = true,
  autoFocus = true,
  restoreFocus = true,
  className = '',
  ...props
}) => {
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);
  const firstFocusableElement = useRef(null);
  const lastFocusableElement = useRef(null);

  // Get all focusable elements within the modal
  const getFocusableElements = useCallback(() => {
    if (!modalRef.current) return [];
    
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])'
    ].join(', ');

    return Array.from(modalRef.current.querySelectorAll(focusableSelectors));
  }, []);

  // Handle focus trap
  const handleKeyDown = useCallback((event) => {
    if (!show) return;

    // ESC key handling
    if (event.key === 'Escape' && keyboard) {
      event.preventDefault();
      onHide();
      return;
    }

    // Tab key handling for focus trap
    if (event.key === 'Tab') {
      const focusableElements = getFocusableElements();
      
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      // Shift + Tab on first element -> go to last
      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
      // Tab on last element -> go to first
      else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }, [show, keyboard, onHide, getFocusableElements]);

  // Set up focus trap when modal opens
  useEffect(() => {
    if (show) {
      // Store the element that had focus before modal opened
      previousActiveElement.current = document.activeElement;

      // Wait for modal to render, then focus first element
      if (autoFocus) {
        setTimeout(() => {
          const focusableElements = getFocusableElements();
          if (focusableElements.length > 0) {
            firstFocusableElement.current = focusableElements[0];
            lastFocusableElement.current = focusableElements[focusableElements.length - 1];
            firstFocusableElement.current.focus();
          }
        }, 100);
      }

      // Add keyboard event listener
      document.addEventListener('keydown', handleKeyDown);
    } else {
      // Restore focus when modal closes
      if (restoreFocus && previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [show, autoFocus, restoreFocus, handleKeyDown, getFocusableElements]);

  return (
    <Modal
      show={show}
      onHide={onHide}
      size={size}
      centered={centered}
      backdrop={backdrop}
      keyboard={keyboard}
      className={className}
      ref={modalRef}
      aria-labelledby="modal-title"
      aria-describedby="modal-body"
      {...props}
    >
      {title && (
        <Modal.Header closeButton>
          <Modal.Title id="modal-title">{title}</Modal.Title>
        </Modal.Header>
      )}
      
      <Modal.Body id="modal-body">
        {children}
      </Modal.Body>
      
      {footer && (
        <Modal.Footer>
          {footer}
        </Modal.Footer>
      )}
    </Modal>
  );
};

AccessibleModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  footer: PropTypes.node,
  size: PropTypes.oneOf(['sm', 'lg', 'xl']),
  centered: PropTypes.bool,
  backdrop: PropTypes.oneOfType([PropTypes.bool, PropTypes.oneOf(['static'])]),
  keyboard: PropTypes.bool,
  autoFocus: PropTypes.bool,
  restoreFocus: PropTypes.bool,
  className: PropTypes.string
};

export default AccessibleModal;

