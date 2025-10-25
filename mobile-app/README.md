# AWS Cost Optimizer - Mobile Application

A React Native mobile application for AWS cost management and optimization.

## 🚀 Features

- **Cross-Platform**: iOS and Android support
- **Real-time Monitoring**: Live cost updates and alerts
- **Interactive Charts**: Mobile-optimized data visualization
- **Biometric Authentication**: Secure login with fingerprint/face ID
- **Offline Support**: Work without internet connection
- **Push Notifications**: Real-time cost alerts
- **Dark Mode**: System preference detection
- **Responsive Design**: Optimized for all screen sizes

## 🛠️ Tech Stack

- **Framework**: React Native 0.72.6
- **Navigation**: React Navigation 6
- **UI**: React Native Paper, React Native Elements
- **Charts**: React Native Chart Kit
- **State Management**: React Query, Context API
- **Storage**: AsyncStorage, Keychain
- **Authentication**: Biometric authentication
- **Networking**: Axios, WebSocket

## 📦 Installation

### Prerequisites

- Node.js >= 16
- React Native CLI
- Xcode (for iOS)
- Android Studio (for Android)
- CocoaPods (for iOS)

### Setup

1. **Install dependencies**:
   ```bash
   cd mobile-app
   npm install
   ```

2. **iOS setup**:
   ```bash
   cd ios && pod install && cd ..
   ```

3. **Android setup**:
   - Open Android Studio
   - Configure Android SDK
   - Set up Android emulator

4. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## 🚀 Running the App

### Development

```bash
# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

### Production

```bash
# Build for Android
npm run build:android

# Build for iOS
npm run build:ios
```

## 📱 App Structure

```
src/
├── components/          # Reusable components
├── screens/            # Screen components
├── navigation/         # Navigation configuration
├── services/           # API and business logic
├── utils/              # Utility functions
├── assets/             # Images, fonts, etc.
└── App.js              # Main app component
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_URL` | Backend API URL | `http://localhost:8000/api` |
| `WS_URL` | WebSocket URL | `ws://localhost:8080/ws` |
| `AWS_REGION` | AWS Region | `us-east-1` |
| `DEBUG` | Debug mode | `true` |

### Feature Flags

- `ENABLE_BIOMETRICS`: Enable biometric authentication
- `ENABLE_PUSH_NOTIFICATIONS`: Enable push notifications
- `ENABLE_OFFLINE_MODE`: Enable offline functionality
- `ENABLE_DARK_MODE`: Enable dark mode support

## 📱 Screens

- **Login**: Authentication with biometric support
- **Dashboard**: Cost overview and key metrics
- **Analytics**: Detailed cost analysis and trends
- **Alerts**: Cost alerts and notifications
- **Settings**: User preferences and configuration
- **Profile**: User profile management

## 🔐 Security Features

- **Biometric Authentication**: Fingerprint and Face ID
- **Secure Storage**: Keychain integration
- **Token Management**: JWT token handling
- **Data Encryption**: Sensitive data protection
- **Certificate Pinning**: API security

## 📊 Performance

- **Lazy Loading**: Screen and component lazy loading
- **Image Optimization**: Optimized image loading
- **Memory Management**: Efficient memory usage
- **Bundle Optimization**: Code splitting and tree shaking
- **Caching**: Intelligent data caching

## 🔔 Notifications

- **Push Notifications**: Real-time cost alerts
- **Local Notifications**: Offline notifications
- **Badge Updates**: Unread alert counts
- **Sound & Vibration**: Custom notification sounds

## 🌙 Dark Mode

- **System Preference**: Automatic dark mode detection
- **Manual Toggle**: User-controlled dark mode
- **Theme Persistence**: Remember user preference
- **Smooth Transitions**: Animated theme changes

## 📱 Offline Support

- **Data Caching**: Store data for offline access
- **Sync Queue**: Queue changes for when online
- **Offline Indicators**: Show connection status
- **Background Sync**: Sync when connection restored

## 🧪 Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

## 📦 Deployment

### Android

1. Generate signed APK:
   ```bash
   cd android
   ./gradlew assembleRelease
   ```

2. Upload to Google Play Store

### iOS

1. Archive in Xcode:
   ```bash
   cd ios
   xcodebuild -workspace AWSCostOptimizer.xcworkspace -scheme AWSCostOptimizer -configuration Release -destination generic/platform=iOS -archivePath AWSCostOptimizer.xcarchive archive
   ```

2. Upload to App Store Connect

## 🔧 Troubleshooting

### Common Issues

1. **Metro bundler issues**:
   ```bash
   npx react-native start --reset-cache
   ```

2. **iOS build issues**:
   ```bash
   cd ios && pod install && cd ..
   ```

3. **Android build issues**:
   ```bash
   cd android && ./gradlew clean && cd ..
   ```

### Debug Mode

```bash
# Enable debug mode
npm start -- --reset-cache
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

---

**AWS Cost Optimizer Mobile App** - Advanced cost management on the go! 📱🎉
