/**
 * Environment Configuration
 */

import Constants from 'expo-constants';

interface AppConfig {
  apiUrl: string;
  appEnv: 'development' | 'staging' | 'production';
  version: string;
  buildNumber: string;
}

const getConfig = (): AppConfig => {
  const expoConfig = Constants.expoConfig;
  
  return {
    apiUrl: process.env.EXPO_PUBLIC_API_URL || 
            (expoConfig?.extra?.apiUrl as string) || 
            'http://localhost:8000',
    appEnv: (process.env.EXPO_PUBLIC_APP_ENV as AppConfig['appEnv']) || 'development',
    version: expoConfig?.version || '1.0.0',
    buildNumber: expoConfig?.ios?.buildNumber || expoConfig?.android?.versionCode?.toString() || '1',
  };
};

export const config = getConfig();

export const isDev = config.appEnv === 'development';
export const isStaging = config.appEnv === 'staging';
export const isProd = config.appEnv === 'production';