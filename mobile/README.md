# DreamCanvas Mobile App

AI-powered image generation mobile app built with React Native and Expo.

## Features

- 🎨 AI image generation with DALL-E
- 💬 Chat with Claude for prompt assistance
- 🖼️ Gallery of generated images
- 👤 User profiles and settings
- 🌙 Dark mode support
- 📱 iOS and Android support

## Tech Stack

- **Framework**: React Native + Expo
- **Navigation**: Expo Router
- **State Management**: Zustand
- **API**: TanStack Query
- **Styling**: NativeWind (Tailwind CSS)
- **Forms**: React Hook Form + Zod

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI
- iOS Simulator (Mac) or Android Emulator

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/dreamcanvas.git
cd dreamcanvas/mobile

# Install dependencies
npm install

# Start the development server
npm start
```

### Running on Device
```bash
# iOS
npm run ios

# Android
npm run android
```

## Project Structure
```
mobile/
├── app/                    # Expo Router screens
│   ├── (auth)/            # Authentication screens
│   ├── (tabs)/            # Main app tabs
│   └── _layout.tsx        # Root layout
├── src/
│   ├── api/               # API client and functions
│   ├── components/        # Reusable components
│   ├── constants/         # App configuration
│   ├── hooks/             # Custom hooks
│   ├── stores/            # Zustand stores
│   ├── types/             # TypeScript types
│   └── utils/             # Utility functions
├── assets/                # Images, fonts, etc.
└── app.json              # Expo configuration
```
## Building for Production
```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build for iOS
npm run build:prod:ios

# Build for Android
npm run build:prod:android
```

## Environment Variables

Create a `.env` file based on `.env.example`:
```bash
EXPO_PUBLIC_API_URL=https://api.dreamcanvas.app
EXPO_PUBLIC_APP_ENV=production
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
