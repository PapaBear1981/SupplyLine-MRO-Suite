# SupplyLine MRO Suite v4.0 - Production Ready

A comprehensive, secure, and scalable Maintenance, Repair, and Operations (MRO) management system built with modern technologies and AWS-ready architecture.

## 🚀 What's New in v4.0

- **JWT Authentication**: Stateless authentication with access and refresh tokens
- **PostgreSQL Database**: Production-ready database with full ACID compliance
- **AWS Deployment**: Cloud-native architecture with auto-scaling capabilities
- **Comprehensive Testing**: Backend unit tests and frontend E2E tests with Playwright
- **Security Hardening**: Input validation, rate limiting, and security headers
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- **Modern Frontend**: Updated React with Redux Toolkit and secure token management

## 🏗️ Architecture

### Backend (Flask + PostgreSQL)
- **Authentication**: JWT-based stateless authentication
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security**: Input validation, rate limiting, security headers
- **Testing**: Comprehensive pytest test suite
- **Deployment**: Docker containers on AWS ECS Fargate

### Frontend (React + Redux)
- **State Management**: Redux Toolkit with JWT token management
- **Routing**: React Router with protected routes
- **Testing**: Playwright E2E tests
- **Deployment**: Static hosting on S3 + CloudFront CDN

### Infrastructure (AWS)
- **Compute**: ECS Fargate for backend containers
- **Database**: RDS PostgreSQL with automated backups
- **Storage**: S3 for frontend assets and file uploads
- **CDN**: CloudFront for global content delivery
- **Security**: Secrets Manager for sensitive configuration
- **Monitoring**: CloudWatch for logs and metrics

## 🔧 Features

### Core Functionality
- **Tool Management**: Complete lifecycle tracking with calibration schedules
- **Chemical Inventory**: Safety compliance and expiration tracking
- **User Management**: Role-based access control with department permissions
- **Checkout System**: Real-time availability tracking with automated notifications
- **Reporting & Analytics**: Comprehensive dashboards and export capabilities
- **Audit Trail**: Complete compliance logging for regulatory requirements

### Security Features
- **JWT Authentication**: Secure, stateless authentication with token refresh
- **Input Validation**: Comprehensive sanitization and validation
- **Rate Limiting**: Protection against brute force and DoS attacks
- **Security Headers**: OWASP-compliant security headers
- **HTTPS Enforcement**: End-to-end encryption in production
- **Account Lockout**: Progressive lockout for failed login attempts

### Operational Features
- **Health Monitoring**: Application and infrastructure health checks
- **Auto-scaling**: Automatic scaling based on demand
- **Backup & Recovery**: Automated database backups with point-in-time recovery
- **Logging**: Structured logging with centralized collection
- **Metrics**: Performance and business metrics collection

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** for backend development
- **Node.js 18+** for frontend development
- **Docker** for containerized development
- **AWS CLI** for deployment (optional)
- **PostgreSQL** for local database (optional)

### Local Development

1. **Clone and Setup**
   ```bash
   git clone https://github.com/your-org/SupplyLine-MRO-Suite.git
   cd SupplyLine-MRO-Suite
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python db_init.py  # Initialize database
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run Development Servers**
   ```bash
   # Terminal 1 - Backend (http://localhost:5000)
   cd backend && python app.py

   # Terminal 2 - Frontend (http://localhost:5173)
   cd frontend && npm run dev
   ```

### Docker Development

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Testing

Run the test suites to verify JWT authentication and application flows.

```bash
# Backend tests (includes JWT refresh)
cd backend && python -m pytest tests/ -v --cov

# Frontend E2E tests with token injection
cd frontend && npm run test:e2e

# All tests
npm run test:all
```

## 🌐 Deployment

### AWS Production Deployment

1. **Prerequisites**
   ```bash
   # Install AWS CLI and configure credentials
   aws configure
   
   # Install required tools
   npm install -g aws-cdk  # Optional: for infrastructure as code
   ```

2. **Automated Deployment**
   ```bash
   # Deploy using the provided script
   ./scripts/deploy.sh
   ```

3. **Manual Deployment**
   See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

4. **CI/CD Deployment**
   - Push to `main` branch triggers automatic deployment
   - GitHub Actions handles testing and deployment
   - Secrets configured in GitHub repository settings

## 📁 Project Structure

```
SupplyLine-MRO-Suite/
├── backend/                    # Flask backend application
│   ├── auth/                  # JWT authentication module
│   ├── security/              # Security middleware and validation
│   ├── tests/                 # Backend test suite
│   ├── models.py              # Database models
│   ├── routes.py              # API routes
│   ├── routes_auth.py         # Authentication routes
│   ├── config.py              # Application configuration
│   ├── app.py                 # Application factory
│   ├── db_init.py             # Database initialization
│   ├── lambda_handler.py      # AWS Lambda handler
│   └── Dockerfile             # Container configuration
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API and auth services
│   │   ├── store/             # Redux store and slices
│   │   └── App.jsx            # Main application
│   ├── tests/e2e/             # Playwright E2E tests
│   ├── playwright.config.js   # E2E test configuration
│   └── package.json           # Dependencies and scripts
├── aws/                       # AWS infrastructure
│   └── cloudformation/        # CloudFormation templates
├── .github/workflows/         # CI/CD pipelines
├── scripts/                   # Deployment and utility scripts
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

## 🔐 Security

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Role-Based Access**: Granular permissions by department and role
- **Token Refresh**: Automatic token renewal for seamless UX
- **Account Lockout**: Progressive lockout for failed attempts

### Data Protection
- **Input Validation**: Comprehensive sanitization and validation
- **SQL Injection Protection**: Parameterized queries with SQLAlchemy
- **XSS Prevention**: Input escaping and Content Security Policy
- **CSRF Protection**: Token-based CSRF protection

### Infrastructure Security
- **HTTPS Enforcement**: End-to-end encryption
- **Security Headers**: OWASP-compliant security headers
- **Network Security**: VPC with private subnets for database
- **Secrets Management**: AWS Secrets Manager for sensitive data

## 📊 Monitoring & Observability

### Application Monitoring
- **Health Checks**: Application and database health endpoints
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Comprehensive error logging and alerting
- **User Activity**: Audit logs for compliance and security

### Infrastructure Monitoring
- **CloudWatch**: Centralized logging and metrics
- **Auto-scaling**: Automatic scaling based on metrics
- **Alerting**: Proactive alerts for issues and anomalies
- **Cost Monitoring**: AWS cost tracking and optimization

## 🧪 Testing Strategy

### Backend Testing
- **Unit Tests**: Comprehensive pytest test suite
- **Integration Tests**: Database and API integration tests
- **Security Tests**: Authentication and authorization tests
- **Performance Tests**: Load testing for critical endpoints

### Frontend Testing
- **E2E Tests**: Playwright tests for user workflows
- **Component Tests**: React component testing
- **Integration Tests**: API integration testing
- **Accessibility Tests**: WCAG compliance testing

### CI/CD Testing
- **Automated Testing**: All tests run on every commit
- **Security Scanning**: Vulnerability scanning in CI/CD
- **Performance Testing**: Automated performance regression tests
- **Deployment Testing**: Smoke tests after deployment

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** your changes (`npm run test:all`)
4. **Commit** your changes (`git commit -m 'Add amazing feature'`)
5. **Push** to the branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

### Development Guidelines
- Follow existing code style and conventions
- Write tests for new features and bug fixes
- Update documentation for API changes
- Ensure security best practices are followed

## 📄 Documentation

- **[Deployment Guide](DEPLOYMENT.md)**: Comprehensive deployment instructions
- **[API Documentation](docs/api.md)**: Complete API reference
- **[Security Guide](docs/security.md)**: Security implementation details
- **[Contributing Guide](CONTRIBUTING.md)**: Development guidelines

## 🆘 Support

### Getting Help
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Check the docs/ folder for detailed guides
- **Security Issues**: Report security vulnerabilities privately

### Troubleshooting
- **Logs**: Check CloudWatch logs for production issues
- **Health Checks**: Use `/health` endpoint for status
- **Database**: Verify database connectivity and migrations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Built with modern security practices and OWASP guidelines
- Designed for scalability and maintainability
- Optimized for AWS cloud deployment
- Comprehensive testing and monitoring included

---

**SupplyLine MRO Suite v4.0** - Production-ready, secure, and scalable MRO management for the modern enterprise.
