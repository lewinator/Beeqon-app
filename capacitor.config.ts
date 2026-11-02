import type { CapacitorConfig } from '@capacitor/cli';

// The app loads the live Beeqon site, so every web release updates the app's screens.
// CAP_DEV=1 points it at the Lovable preview instead (testing only).
const dev = process.env.CAP_DEV === '1';

const config: CapacitorConfig = {
  appId: 'za.co.beeqon.app',
  appName: 'Beeqon',
  // Offline fallback page only; the real screens come from server.url.
  webDir: 'android-shell',
  server: {
    url: dev
      ? 'https://fbb80337-ed44-4d02-820b-2e038aa621d0.lovableproject.com?forceHideBadge=true'
      : 'https://beeqon.co.za/auth',
    allowNavigation: ['beeqon.co.za', 'www.beeqon.co.za', '*.lovableproject.com'],
    cleartext: false,
  },
  plugins: {
    SplashScreen: { launchShowDuration: 1200, backgroundColor: '#0B1220', showSpinner: false },
    StatusBar: { backgroundColor: '#0B1220' },
  },
  android: { allowMixedContent: false },
};

export default config;
