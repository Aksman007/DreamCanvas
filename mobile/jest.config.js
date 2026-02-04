module.exports = {
    preset: 'jest-expo',
    setupFilesAfterEnv: [
        '@testing-library/jest-native/extend-expect',
        '<rootDir>/jest.setup.js',
    ],
    transformIgnorePatterns: [
        'node_modules/(?!(jest-)?react-native|@react-native|@react-native-community|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg|nativewind|react-native-css-interop|react-native-reanimated|lucide-react-native|zustand|@tanstack)',
    ],
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
    },
    testMatch: [
        '**/__tests__/**/*.test.[jt]s?(x)',
        '**/*.test.[jt]s?(x)',
    ],
    testPathIgnorePatterns: [
        '/node_modules/',
        '<rootDir>/src/__tests__/mocks/',
        '<rootDir>/src/__tests__/utils/',
    ],
    collectCoverageFrom: [
        'src/**/*.{ts,tsx}',
        '!src/**/*.d.ts',
        '!src/types/**',
        '!src/__tests__/**',
    ],
    testEnvironment: 'node',
    moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
    globals: {
        __DEV__: true,
    },
    clearMocks: true,
    resetMocks: false,
};