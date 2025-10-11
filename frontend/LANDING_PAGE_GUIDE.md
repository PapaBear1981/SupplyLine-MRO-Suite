# SupplyLine MRO Suite - Landing Page Documentation

## Overview
This document provides guidance on customizing and maintaining the landing page for the SupplyLine MRO Suite application.

## File Structure

```
frontend/src/
├── pages/
│   ├── LandingPage.jsx       # Main landing page component
│   └── LandingPage.css        # Landing page styles
├── App.jsx                    # Updated with landing page routing
└── index.html                 # Updated with SEO meta tags
```

## Features Implemented

### 1. Navigation Bar (Sticky/Fixed)
- **Location**: Top of the page, fixed position
- **Features**:
  - Logo/branding on the left
  - Navigation links (About, Features, Testimonials, Contact)
  - Login button on the right
  - Smooth scroll behavior
  - Background blur effect on scroll
  - Responsive hamburger menu for mobile

### 2. Hero Section
- **Features**:
  - Full viewport height (100vh)
  - Animated gradient background
  - Compelling headline with gradient text effect
  - Two CTAs: "Get Started" and "Login"
  - Fade-in animations with staggered timing
  - Scroll indicator with bounce animation

### 3. About Us Section
- **Features**:
  - 2-column layout (text + image)
  - Fade-in animation on scroll
  - Placeholder image from Unsplash
  - Hover effect on image

### 4. Features Section
- **Features**:
  - 6 feature cards in a 3x2 grid
  - Icons from React Icons (FontAwesome)
  - Hover effects: scale, glow, color shifts
  - Staggered fade-in animations
  - Gradient overlay on hover

### 5. Testimonials Section
- **Features**:
  - 4 testimonial cards in a 2x2 grid
  - Avatar placeholders with initials
  - Quote styling
  - Hover effects with border animation

### 6. Contact Section
- **Features**:
  - Contact form with validation
  - Fields: Name, Email, Company (optional), Message
  - Loading state animation
  - Success message display
  - Contact information (email, phone)
  - Form submission simulation (replace with actual API)

### 7. Footer
- **Features**:
  - Copyright information
  - Quick links (Login, Register, Privacy, Terms)
  - Social media icons (LinkedIn, Twitter, GitHub)
  - Back to top button (appears on scroll)

## Customization Guide

### Updating Content

#### Hero Section
Edit `frontend/src/pages/LandingPage.jsx` around line 220:
```jsx
<h1 className="hero-title fade-in stagger-1">
  Your Custom Headline Here
</h1>
<p className="hero-subtitle fade-in stagger-2">
  Your custom subtitle here
</p>
```

#### Features
Edit the `features` array in `LandingPage.jsx` around line 130:
```jsx
const features = [
  {
    icon: <FaTools />,
    title: 'Your Feature Title',
    description: 'Your feature description'
  },
  // Add more features...
];
```

#### Testimonials
Edit the `testimonials` array in `LandingPage.jsx` around line 155:
```jsx
const testimonials = [
  {
    quote: "Your testimonial quote",
    name: "Customer Name",
    role: "Job Title",
    company: "Company Name"
  },
  // Add more testimonials...
];
```

### Replacing Placeholder Images

#### About Section Image
Replace the Unsplash URL in `LandingPage.jsx` around line 270:
```jsx
<img 
  src="YOUR_IMAGE_URL_HERE" 
  alt="Your alt text" 
  className="img-fluid rounded shadow-lg"
/>
```

**Recommended image themes**:
- Industrial equipment
- Warehouse operations
- Supply chain management
- Technology interfaces
- Manufacturing facilities

**Image specifications**:
- Recommended size: 800x600px or larger
- Format: WebP with JPG fallback for best performance
- Aspect ratio: 4:3 or 16:9

### Customizing Colors

Edit `frontend/src/pages/LandingPage.css` CSS variables (lines 6-18):
```css
:root {
  --bg-dark-primary: #0a0a0a;        /* Main background */
  --bg-dark-secondary: #121212;      /* Section backgrounds */
  --accent-blue: #0066ff;            /* Primary accent color */
  --accent-blue-light: #00a3ff;      /* Secondary accent color */
  --accent-silver: #c0c0c0;          /* Silver accent */
  --text-primary: #ffffff;           /* Primary text */
  --text-secondary: #b0b0b0;         /* Secondary text */
}
```

### Customizing Animations

#### Animation Duration
Edit transition durations in `LandingPage.css`:
```css
.fade-in {
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### Stagger Delays
Adjust stagger timing in `LandingPage.css` around line 220:
```css
.stagger-1 { transition-delay: 0.1s; }
.stagger-2 { transition-delay: 0.3s; }
.stagger-3 { transition-delay: 0.5s; }
```

### Form Integration

#### Connecting to Backend API
Replace the form submission simulation in `LandingPage.jsx` around line 105:

```jsx
const handleFormSubmit = async (e) => {
  e.preventDefault();
  setIsSubmitting(true);
  setFormError('');

  // Validation...

  try {
    // Replace with your actual API endpoint
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      setFormSubmitted(true);
      setFormData({ name: '', email: '', company: '', message: '' });
    } else {
      setFormError('Failed to send message. Please try again.');
    }
  } catch (error) {
    setFormError('An error occurred. Please try again later.');
  } finally {
    setIsSubmitting(false);
  }
};
```

## Responsive Breakpoints

The landing page uses the following breakpoints:

- **Desktop**: > 1024px
- **Tablet**: 768px - 1024px
- **Mobile**: < 768px
- **Small Mobile**: < 375px

## Accessibility Features

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus states on all interactive elements
- Reduced motion support for users with motion sensitivity
- High contrast mode support
- Proper heading hierarchy

## Performance Optimizations

- CSS transforms and opacity for GPU-accelerated animations
- Intersection Observer API for scroll animations
- Lazy loading for images below the fold
- Optimized image formats (WebP recommended)
- Debounced scroll event listeners
- `will-change` property for animated elements

## Testing Checklist

### Functionality
- [ ] All navigation links scroll to correct sections
- [ ] Login button navigates to `/login`
- [ ] Get Started button navigates to `/register`
- [ ] Contact form validation works
- [ ] Form submission shows loading state
- [ ] Success message displays after submission
- [ ] Back to top button appears on scroll
- [ ] Back to top button scrolls to top

### Responsive Design
- [ ] Test at 375px (mobile)
- [ ] Test at 768px (tablet)
- [ ] Test at 1024px (desktop)
- [ ] Test at 1440px (large desktop)
- [ ] Hamburger menu works on mobile
- [ ] All sections stack properly on mobile

### Animations
- [ ] Hero section fade-in animations work
- [ ] Scroll-triggered animations activate
- [ ] Feature cards animate on hover
- [ ] Testimonial cards animate on hover
- [ ] Gradient background animates
- [ ] Scroll indicator bounces

### Browser Compatibility
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Accessibility
- [ ] Keyboard navigation works
- [ ] Focus states are visible
- [ ] Screen reader compatibility
- [ ] Color contrast meets WCAG AA standards

## Common Issues & Solutions

### Issue: Animations not triggering on scroll
**Solution**: Check that the Intersection Observer is properly initialized and elements have the `fade-in` class.

### Issue: Images not loading
**Solution**: Verify image URLs are correct and accessible. Use absolute URLs for external images.

### Issue: Form not submitting
**Solution**: Check browser console for errors. Ensure form validation is passing.

### Issue: Navbar not changing on scroll
**Solution**: Verify the scroll event listener is attached and the `scrolled` state is updating.

## Future Enhancements

Consider adding:
- Parallax scrolling effects
- Video background in hero section
- Interactive demos or screenshots
- Customer logo carousel
- Live chat integration
- Newsletter signup
- Pricing section
- FAQ section
- Blog/resources section

## Support

For questions or issues with the landing page, please refer to:
- Main README.md in the project root
- React documentation: https://react.dev
- React Bootstrap documentation: https://react-bootstrap.github.io
- React Icons documentation: https://react-icons.github.io/react-icons

## Version History

- **v1.0.0** (2025-10-11): Initial landing page implementation
  - Dark, modern design with gradient effects
  - Full responsive support
  - Scroll animations
  - Contact form with validation
  - SEO meta tags

