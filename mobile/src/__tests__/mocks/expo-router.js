module.exports = {
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
    Link: ({ children }) => children,
    Redirect: () => null,
    Slot: ({ children }) => children,
    Stack: Object.assign(({ children }) => children, {
        Screen: () => null,
    }),
    Tabs: Object.assign(({ children }) => children, {
        Screen: () => null,
    }),
    useFocusEffect: jest.fn(),
};