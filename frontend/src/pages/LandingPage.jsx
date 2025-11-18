import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Container, Row, Col, Card, Form, Button, Navbar, Nav } from 'react-bootstrap';
import {
  FaTools, FaChartLine, FaShieldAlt, FaFlask,
  FaClipboardCheck, FaWarehouse, FaBarcode, FaShoppingCart,
  FaBox, FaArrowDown, FaArrowUp,
  FaEnvelope, FaPhone, FaLinkedin, FaTwitter, FaGithub
} from 'react-icons/fa';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state) => state.auth);
  const [scrolled, setScrolled] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: ''
  });
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Intersection Observer for scroll animations
  const observerRef = useRef(null);

  useEffect(() => {
    // Redirect if already authenticated
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    // Handle scroll for navbar background
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // Intersection Observer for fade-in animations
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      { threshold: 0.1 }
    );

    // Observe all elements with fade-in class
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach((el) => observerRef.current.observe(el));

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFormChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setFormError('');
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setFormError('');

    // Basic validation
    if (!formData.name || !formData.email || !formData.message) {
      setFormError('Please fill in all required fields');
      setIsSubmitting(false);
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setFormError('Please enter a valid email address');
      setIsSubmitting(false);
      return;
    }

    // Simulate form submission (replace with actual API call)
    setTimeout(() => {
      setFormSubmitted(true);
      setIsSubmitting(false);
      setFormData({ name: '', email: '', company: '', message: '' });
      
      // Reset success message after 5 seconds
      setTimeout(() => setFormSubmitted(false), 5000);
    }, 1500);
  };

  const features = [
    {
      icon: <FaTools />,
      title: 'Tool Management',
      description: 'Complete tool inventory tracking with checkout/return system, calibration scheduling, and multi-serial number support.'
    },
    {
      icon: <FaFlask />,
      title: 'Chemical Management',
      description: 'Track chemicals by part number, lot, and expiration. Automated reorder requests, child lot creation, and compliance tracking.'
    },
    {
      icon: <FaWarehouse />,
      title: 'Kit & Warehouse System',
      description: 'Mobile warehouse kits for aircraft support. Manage boxes, transfers, issuances, and kit-to-kit transactions.'
    },
    {
      icon: <FaBarcode />,
      title: 'Barcode & QR Labels',
      description: 'Professional PDF labels with barcodes and QR codes. Mobile-friendly landing pages for quick item lookup and tracking.'
    },
    {
      icon: <FaShoppingCart />,
      title: 'Procurement & Ordering',
      description: 'Automated reorder requests from low stock. Track chemicals on order and streamline procurement workflows.'
    },
    {
      icon: <FaChartLine />,
      title: 'Analytics & Reporting',
      description: 'Comprehensive reports on tool usage, chemical waste, shelf life analytics, and department distribution with export options.'
    },
    {
      icon: <FaClipboardCheck />,
      title: 'Calibration Tracking',
      description: 'Automated calibration scheduling, standards management, and overdue alerts to maintain compliance and quality.'
    },
    {
      icon: <FaShieldAlt />,
      title: 'Security & RBAC',
      description: 'Role-based access control with JWT authentication, full audit trails, and configurable permissions for Admin, Materials, and Maintenance roles.'
    },
    {
      icon: <FaBox />,
      title: 'Expendables Management',
      description: 'Track consumables with lot/serial numbers. Streamlined warehouse-to-kit transfers with auto-complete functionality.'
    }
  ];

  const testimonials = [
    {
      quote: "The chemical management system with automated expiration tracking and child lot creation has eliminated waste and improved our compliance. The barcode labels make everything traceable.",
      name: "Sarah Johnson",
      role: "Materials Manager",
      company: "Regional Aviation Services"
    },
    {
      quote: "Managing mobile warehouse kits for our Q400 and CL415 fleet used to be a nightmare. SupplyLine's kit transfer system and issuance tracking have streamlined our entire operation.",
      name: "Michael Chen",
      role: "Fleet Maintenance Supervisor",
      company: "Northern Air Operations"
    },
    {
      quote: "The automated reorder requests from chemical issuance have cut our procurement cycle time in half. We always know what's on order and what needs reordering.",
      name: "David Martinez",
      role: "Procurement Specialist",
      company: "Aerospace Supply Solutions"
    },
    {
      quote: "Having tools, chemicals, kits, and expendables all in one system is a game-changer. The analytics give us visibility we never had before, and the RBAC keeps everything secure.",
      name: "Emily Thompson",
      role: "MRO Operations Director",
      company: "Continental Aircraft Maintenance"
    }
  ];

  return (
    <div className="landing-page">
      {/* Navigation Bar */}
      <Navbar 
        expand="lg" 
        fixed="top" 
        className={`landing-navbar ${scrolled ? 'scrolled' : ''}`}
      >
        <Container>
          <Navbar.Brand className="brand-logo">
            <FaTools className="me-2" />
            SupplyLine MRO Suite
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="landing-navbar-nav" />
          <Navbar.Collapse id="landing-navbar-nav">
            <Nav className="ms-auto align-items-center">
              <Nav.Link onClick={() => scrollToSection('about')}>About</Nav.Link>
              <Nav.Link onClick={() => scrollToSection('features')}>Features</Nav.Link>
              <Nav.Link onClick={() => scrollToSection('testimonials')}>Testimonials</Nav.Link>
              <Nav.Link onClick={() => scrollToSection('contact')}>Contact</Nav.Link>
              <Link to="/login" className="btn btn-login ms-3">
                Login
              </Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-background"></div>
        <Container className="hero-content">
          <Row className="align-items-center min-vh-100">
            <Col lg={8} className="mx-auto text-center">
              <h1 className="hero-title fade-in stagger-1">
                Complete MRO Suite for Aerospace & Manufacturing
              </h1>
              <p className="hero-subtitle fade-in stagger-2">
                Comprehensive platform for managing tools, chemicals, kits, and warehouses.
                From inventory tracking to procurement, barcode labels to analytics—everything your MRO operations need in one powerful suite.
              </p>
              <div className="hero-cta fade-in stagger-3">
                <Link to="/register" className="btn btn-primary btn-lg me-3">
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-outline-light btn-lg">
                  Login
                </Link>
              </div>
            </Col>
          </Row>
          <div className="scroll-indicator" onClick={() => scrollToSection('about')}>
            <FaArrowDown className="bounce" />
          </div>
        </Container>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <Container>
          <Row className="align-items-center">
            <Col lg={6} className="fade-in">
              <h2 className="section-title">About SupplyLine MRO Suite</h2>
              <p className="section-text">
                SupplyLine MRO Suite is an enterprise-grade platform designed for aerospace and manufacturing
                MRO operations. We provide unified management of tools, chemicals, mobile warehouse kits,
                expendables, and procurement—all in one integrated system.
              </p>
              <p className="section-text">
                From tracking tool calibrations and chemical expiration dates to managing mobile warehouse
                kits for aircraft maintenance, our platform handles the complexity of modern MRO operations.
                Features like automated reorder requests, barcode/QR label generation, and comprehensive
                analytics help you maintain compliance while optimizing efficiency.
              </p>
              <p className="section-text">
                Built with React and Flask, deployed via Docker, and designed for real-world aerospace
                environments, SupplyLine delivers the reliability and scalability your operations demand.
                Whether you're managing Q400, RJ85, or CL415 aircraft kits, or tracking chemicals across
                multiple warehouses, SupplyLine has you covered.
              </p>
            </Col>
            <Col lg={6} className="fade-in">
              <div className="about-image-placeholder">
                <img 
                  src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=600&fit=crop" 
                  alt="Modern warehouse operations" 
                  className="img-fluid rounded shadow-lg"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <Container>
          <h2 className="section-title text-center fade-in">Comprehensive Feature Set</h2>
          <p className="section-subtitle text-center fade-in">
            Everything you need to manage tools, chemicals, kits, warehouses, and procurement in one unified platform
          </p>
          <Row className="g-4 mt-4">
            {features.map((feature, index) => (
              <Col key={index} lg={4} md={6} className="fade-in" style={{ '--stagger': index }}>
                <Card className="feature-card h-100">
                  <Card.Body className="text-center">
                    <div className="feature-icon">
                      {feature.icon}
                    </div>
                    <h3 className="feature-title">{feature.title}</h3>
                    <p className="feature-description">{feature.description}</p>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </Container>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials-section">
        <Container>
          <h2 className="section-title text-center fade-in">What Our Clients Say</h2>
          <p className="section-subtitle text-center fade-in">
            Trusted by organizations worldwide
          </p>
          <Row className="g-4 mt-4">
            {testimonials.map((testimonial, index) => (
              <Col key={index} lg={6} className="fade-in" style={{ '--stagger': index }}>
                <Card className="testimonial-card h-100">
                  <Card.Body>
                    <div className="quote-icon">"</div>
                    <p className="testimonial-quote">{testimonial.quote}</p>
                    <div className="testimonial-author">
                      <div className="author-avatar">
                        {testimonial.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div className="author-info">
                        <h4 className="author-name">{testimonial.name}</h4>
                        <p className="author-role">{testimonial.role}</p>
                        <p className="author-company">{testimonial.company}</p>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </Container>
      </section>

      {/* Contact Section */}
      <section id="contact" className="contact-section">
        <Container>
          <Row>
            <Col lg={6} className="fade-in">
              <h2 className="section-title">Get In Touch</h2>
              <p className="section-text">
                Have questions about SupplyLine MRO Suite? We'd love to hear from you.
                Fill out the form and our team will get back to you within 24 hours.
              </p>
              <div className="contact-info mt-4">
                <div className="contact-item">
                  <FaEnvelope className="contact-icon" />
                  <div>
                    <h5>Email</h5>
                    <p>info@supplyline-mro.com</p>
                  </div>
                </div>
                <div className="contact-item">
                  <FaPhone className="contact-icon" />
                  <div>
                    <h5>Phone</h5>
                    <p>+1 (555) 123-4567</p>
                  </div>
                </div>
              </div>
            </Col>
            <Col lg={6} className="fade-in">
              <Card className="contact-form-card">
                <Card.Body>
                  {formSubmitted ? (
                    <div className="success-message">
                      <div className="success-icon">✓</div>
                      <h3>Thank You!</h3>
                      <p>Your message has been sent successfully. We'll be in touch soon.</p>
                    </div>
                  ) : (
                    <Form onSubmit={handleFormSubmit}>
                      <Form.Group className="mb-3">
                        <Form.Label>Name *</Form.Label>
                        <Form.Control
                          type="text"
                          name="name"
                          value={formData.name}
                          onChange={handleFormChange}
                          placeholder="Your name"
                          required
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Label>Email *</Form.Label>
                        <Form.Control
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleFormChange}
                          placeholder="your.email@company.com"
                          required
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Label>Company</Form.Label>
                        <Form.Control
                          type="text"
                          name="company"
                          value={formData.company}
                          onChange={handleFormChange}
                          placeholder="Your company name"
                        />
                      </Form.Group>
                      <Form.Group className="mb-3">
                        <Form.Label>Message *</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={4}
                          name="message"
                          value={formData.message}
                          onChange={handleFormChange}
                          placeholder="Tell us about your needs..."
                          required
                        />
                      </Form.Group>
                      {formError && (
                        <div className="alert alert-danger">{formError}</div>
                      )}
                      <Button
                        type="submit"
                        className="btn-submit w-100"
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" />
                            Sending...
                          </>
                        ) : (
                          'Send Message'
                        )}
                      </Button>
                    </Form>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <Container>
          <Row className="py-4">
            <Col lg={4} md={6} className="mb-4 mb-lg-0">
              <h5 className="footer-brand">
                <FaTools className="me-2" />
                SupplyLine MRO Suite
              </h5>
              <p className="footer-text">
                Enterprise MRO platform for managing tools, chemicals, kits, warehouses, and procurement operations.
              </p>
            </Col>
            <Col lg={4} md={6} className="mb-4 mb-lg-0">
              <h5 className="footer-heading">Quick Links</h5>
              <ul className="footer-links">
                <li><Link to="/login">Login</Link></li>
                <li><Link to="/register">Register</Link></li>
                <li><a href="#privacy">Privacy Policy</a></li>
                <li><a href="#terms">Terms of Service</a></li>
              </ul>
            </Col>
            <Col lg={4} md={12}>
              <h5 className="footer-heading">Connect With Us</h5>
              <div className="social-links">
                <a href="#linkedin" aria-label="LinkedIn">
                  <FaLinkedin />
                </a>
                <a href="#twitter" aria-label="Twitter">
                  <FaTwitter />
                </a>
                <a href="#github" aria-label="GitHub">
                  <FaGithub />
                </a>
              </div>
            </Col>
          </Row>
          <hr className="footer-divider" />
          <Row>
            <Col className="text-center">
              <p className="footer-copyright">
                &copy; {new Date().getFullYear()} SupplyLine MRO Suite. All rights reserved.
              </p>
            </Col>
          </Row>
        </Container>

        {/* Back to Top Button */}
        <button
          className={`back-to-top ${scrolled ? 'visible' : ''}`}
          onClick={scrollToTop}
          aria-label="Back to top"
        >
          <FaArrowUp />
        </button>
      </footer>
    </div>
  );
};

export default LandingPage;

