const React = require('react');
const { View } = require('react-native');

const Image = React.forwardRef((props, ref) => {
    return React.createElement(View, { ...props, ref, testID: props.testID || 'expo-image' });
});

Image.displayName = 'ExpoImage';

module.exports = {
    Image,
};