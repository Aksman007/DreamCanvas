/* eslint-disable no-undef */
import '@testing-library/jest-native/extend-expect';

// Mock __DEV__
global.__DEV__ = true;

// Polyfill fetch
global.fetch = jest.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve({}),
        ok: true,
    })
);

// Mock expo-secure-store
jest.mock('expo-secure-store', () => ({
    getItemAsync: jest.fn(() => Promise.resolve(null)),
    setItemAsync: jest.fn(() => Promise.resolve()),
    deleteItemAsync: jest.fn(() => Promise.resolve()),
}));

// Mock expo-haptics
jest.mock('expo-haptics', () => ({
    impactAsync: jest.fn(),
    notificationAsync: jest.fn(),
    selectionAsync: jest.fn(),
    ImpactFeedbackStyle: {
        Light: 'light',
        Medium: 'medium',
        Heavy: 'heavy',
    },
    NotificationFeedbackType: {
        Success: 'success',
        Warning: 'warning',
        Error: 'error',
    },
}));

// Mock expo-image-picker
jest.mock('expo-image-picker', () => ({
    requestMediaLibraryPermissionsAsync: jest.fn(() =>
        Promise.resolve({ status: 'granted' })
    ),
    requestCameraPermissionsAsync: jest.fn(() =>
        Promise.resolve({ status: 'granted' })
    ),
    launchImageLibraryAsync: jest.fn(() =>
        Promise.resolve({ canceled: true, assets: [] })
    ),
    launchCameraAsync: jest.fn(() =>
        Promise.resolve({ canceled: true, assets: [] })
    ),
    MediaTypeOptions: {
        Images: 'Images',
    },
}));

// Mock expo-media-library
jest.mock('expo-media-library', () => ({
    requestPermissionsAsync: jest.fn(() =>
        Promise.resolve({ status: 'granted' })
    ),
    saveToLibraryAsync: jest.fn(() => Promise.resolve()),
}));

// Mock expo-file-system
jest.mock('expo-file-system', () => ({
    documentDirectory: '/mock/document/directory/',
    downloadAsync: jest.fn(() => Promise.resolve({ uri: '/mock/file.png' })),
    deleteAsync: jest.fn(() => Promise.resolve()),
}));

// Mock @react-native-async-storage/async-storage
jest.mock('@react-native-async-storage/async-storage', () => ({
    setItem: jest.fn(() => Promise.resolve()),
    getItem: jest.fn(() => Promise.resolve(null)),
    removeItem: jest.fn(() => Promise.resolve()),
    clear: jest.fn(() => Promise.resolve()),
    getAllKeys: jest.fn(() => Promise.resolve([])),
    multiGet: jest.fn(() => Promise.resolve([])),
    multiSet: jest.fn(() => Promise.resolve()),
    multiRemove: jest.fn(() => Promise.resolve()),
}));

// Mock @react-native-community/netinfo
jest.mock('@react-native-community/netinfo', () => ({
    addEventListener: jest.fn(() => jest.fn()),
    fetch: jest.fn(() =>
        Promise.resolve({
            isConnected: true,
            isInternetReachable: true,
            type: 'wifi',
        })
    ),
}));

// Mock expo-blur
jest.mock('expo-blur', () => ({
    BlurView: 'BlurView',
}));

// Mock expo-constants
jest.mock('expo-constants', () => ({
    expoConfig: {
        name: 'DreamCanvas',
        version: '1.0.0',
        extra: {},
    },
}));

// Mock expo-image
jest.mock('expo-image', () => ({
    Image: 'ExpoImage',
}));

// Mock expo-router
jest.mock('expo-router', () => ({
    router: {
        push: jest.fn(),
        replace: jest.fn(),
        back: jest.fn(),
        canGoBack: jest.fn(() => true),
        setParams: jest.fn(),
    },
    useRouter: () => ({
        push: jest.fn(),
        replace: jest.fn(),
        back: jest.fn(),
        canGoBack: jest.fn(() => true),
        setParams: jest.fn(),
    }),
    useLocalSearchParams: jest.fn(() => ({})),
    useNavigation: jest.fn(() => ({
        canGoBack: jest.fn(() => true),
        goBack: jest.fn(),
        navigate: jest.fn(),
    })),
    useSegments: jest.fn(() => []),
    usePathname: jest.fn(() => '/'),
    useFocusEffect: jest.fn(),
    Link: 'Link',
    Redirect: 'Redirect',
    Slot: 'Slot',
    Stack: { Screen: 'Screen' },
    Tabs: { Screen: 'Screen' },
}));

// Mock react-native-safe-area-context
jest.mock('react-native-safe-area-context', () => ({
    SafeAreaProvider: 'SafeAreaProvider',
    SafeAreaView: 'SafeAreaView',
    useSafeAreaInsets: () => ({ top: 0, right: 0, bottom: 0, left: 0 }),
    useSafeAreaFrame: () => ({ x: 0, y: 0, width: 390, height: 844 }),
}));

// Mock react-native-gesture-handler
jest.mock('react-native-gesture-handler', () => ({
    GestureHandlerRootView: 'GestureHandlerRootView',
    Swipeable: 'Swipeable',
    DrawerLayout: 'DrawerLayout',
    State: {},
    ScrollView: 'ScrollView',
    Slider: 'Slider',
    Switch: 'Switch',
    TextInput: 'TextInput',
    ToolbarAndroid: 'ToolbarAndroid',
    ViewPagerAndroid: 'ViewPagerAndroid',
    DrawerLayoutAndroid: 'DrawerLayoutAndroid',
    WebView: 'WebView',
    NativeViewGestureHandler: 'NativeViewGestureHandler',
    TapGestureHandler: 'TapGestureHandler',
    FlingGestureHandler: 'FlingGestureHandler',
    ForceTouchGestureHandler: 'ForceTouchGestureHandler',
    LongPressGestureHandler: 'LongPressGestureHandler',
    PanGestureHandler: 'PanGestureHandler',
    PinchGestureHandler: 'PinchGestureHandler',
    RotationGestureHandler: 'RotationGestureHandler',
    RawButton: 'RawButton',
    BaseButton: 'BaseButton',
    RectButton: 'RectButton',
    BorderlessButton: 'BorderlessButton',
    FlatList: 'FlatList',
    gestureHandlerRootHOC: jest.fn((component) => component),
    Directions: {},
}));

// Mock react-native-reanimated
jest.mock('react-native-reanimated', () => ({
    default: {
        createAnimatedComponent: jest.fn((component) => component),
        View: 'Animated.View',
        Text: 'Animated.Text',
        call: jest.fn(),
    },
    useSharedValue: jest.fn((init) => ({ value: init })),
    useAnimatedStyle: jest.fn(() => ({})),
    withTiming: jest.fn((val) => val),
    withSpring: jest.fn((val) => val),
    withSequence: jest.fn((...args) => args[0]),
    withDelay: jest.fn((_, val) => val),
    withRepeat: jest.fn((val) => val),
    Easing: {
        linear: jest.fn(),
        ease: jest.fn(),
        inOut: jest.fn(() => jest.fn()),
    },
    runOnJS: jest.fn((fn) => fn),
    useAnimatedRef: jest.fn(() => ({ current: null })),
    useDerivedValue: jest.fn((fn) => ({ value: typeof fn === 'function' ? 0 : fn })),
    createAnimatedComponent: jest.fn((component) => component),
}));

// Mock nativewind
jest.mock('nativewind', () => ({
    styled: jest.fn((component) => component),
    useColorScheme: () => ({ colorScheme: 'light', setColorScheme: jest.fn() }),
}));

// Mock react-native-css-interop
jest.mock('react-native-css-interop', () => ({
    cssInterop: jest.fn(),
    remapProps: jest.fn(),
}));

// Mock lucide-react-native - use a simple object with string values
jest.mock('lucide-react-native', () =>
    new Proxy({}, {
        get: (_, prop) => prop.toString(),
    })
);

// Silence specific warnings
const originalWarn = console.warn;
const originalError = console.error;

console.warn = (...args) => {
    const message = args[0];
    if (
        typeof message === 'string' &&
        (message.includes('Animated:') ||
            message.includes('componentWillReceiveProps') ||
            message.includes('componentWillMount'))
    ) {
        return;
    }
    originalWarn.apply(console, args);
};

console.error = (...args) => {
    const message = args[0];
    if (
        typeof message === 'string' &&
        (message.includes('Warning:') ||
            message.includes('act(...)'))
    ) {
        return;
    }
    originalError.apply(console, args);
};

// Global test timeout
jest.setTimeout(10000);