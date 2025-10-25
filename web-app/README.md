# AWS Cost Optimizer - Web Application

A modern React web application for AWS cost management and optimization.

## 🚀 Features

- **Real-time Dashboard**: Live cost monitoring and analytics
- **Interactive Charts**: Advanced data visualization with Recharts
- **Cost Analytics**: Detailed cost breakdown and trends
- **Alert Management**: Cost alerts and notifications
- **Optimization Recommendations**: AI-powered cost savings suggestions
- **Responsive Design**: Mobile-first, responsive UI
- **Real-time Updates**: WebSocket integration for live data
- **Offline Support**: Progressive Web App capabilities

## 🛠️ Tech Stack

- **Frontend**: React 18, React Router, React Query
- **UI**: Tailwind CSS, Framer Motion, Lucide React
- **Charts**: Recharts
- **State Management**: React Query, Context API
- **Real-time**: WebSocket
- **Build Tool**: Create React App

## 📦 Installation

1. **Install dependencies**:
   ```bash
   cd web-app
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000/api` |
| `REACT_APP_WS_URL` | WebSocket URL | `ws://localhost:8080/ws` |
| `REACT_APP_AWS_REGION` | AWS Region | `us-east-1` |
| `REACT_APP_DEBUG` | Debug mode | `true` |
| `REACT_APP_MOCK_DATA` | Use mock data | `true` |

### Feature Flags

- `REACT_APP_ENABLE_ANALYTICS`: Enable analytics features
- `REACT_APP_ENABLE_ALERTS`: Enable alert management
- `REACT_APP_ENABLE_OPTIMIZATION`: Enable optimization recommendations
- `REACT_APP_ENABLE_REAL_TIME`: Enable real-time updates

## 📱 Pages

- **Dashboard**: Overview and key metrics
- **Analytics**: Detailed cost analysis and trends
- **Alerts**: Cost alerts and notifications
- **Settings**: User preferences and configuration

## 🔌 API Integration

The application integrates with the AWS Cost Optimizer backend API:

- **Authentication**: JWT-based authentication
- **Real-time**: WebSocket for live updates
- **Data Fetching**: React Query for efficient data management
- **Error Handling**: Comprehensive error handling and user feedback

## 🎨 UI Components

- **Responsive Design**: Mobile-first approach
- **Dark Mode**: System preference detection
- **Animations**: Smooth transitions with Framer Motion
- **Accessibility**: WCAG 2.1 compliant
- **Loading States**: Skeleton loaders and spinners

## 🚀 Deployment

### Development
```bash
npm start
```

### Production
```bash
npm run build
npm run serve
```

### Docker
```bash
docker build -t aws-cost-optimizer-web .
docker run -p 3000:3000 aws-cost-optimizer-web
```

## 📊 Performance

- **Bundle Size**: Optimized with code splitting
- **Loading**: Lazy loading for routes and components
- **Caching**: React Query for intelligent caching
- **PWA**: Service worker for offline support

## 🔒 Security

- **Authentication**: Secure JWT token handling
- **HTTPS**: SSL/TLS encryption
- **CORS**: Proper cross-origin configuration
- **XSS Protection**: Content Security Policy

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## 📈 Monitoring

- **Error Tracking**: Comprehensive error logging
- **Performance**: Web Vitals monitoring
- **Analytics**: User interaction tracking
- **Real-time**: WebSocket connection monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

---

**AWS Cost Optimizer Web Application** - Advanced cost management made simple! 🎉
