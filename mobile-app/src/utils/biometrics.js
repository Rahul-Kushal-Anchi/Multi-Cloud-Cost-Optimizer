import * as Keychain from 'react-native-keychain';
import { Alert } from 'react-native';

export const checkBiometrics = async () => {
  try {
    const biometrics = await Keychain.getSupportedBiometryType();
    return {
      available: !!biometrics,
      type: biometrics,
    };
  } catch (error) {
    console.error('Biometrics check error:', error);
    return {
      available: false,
      type: null,
    };
  }
};

export const authenticateWithBiometrics = async (prompt = 'Authenticate') => {
  try {
    const biometrics = await checkBiometrics();
    
    if (!biometrics.available) {
      throw new Error('Biometrics not available on this device');
    }

    const result = await Keychain.authenticate({
      promptTitle: prompt,
      promptSubtitle: 'Use your biometric to authenticate',
      promptDescription: 'Use your fingerprint or face to authenticate',
      cancelButton: 'Cancel',
      fallbackPrompt: 'Use Passcode',
    });

    return result;
  } catch (error) {
    if (error.message.includes('UserCancel')) {
      throw new Error('Authentication cancelled by user');
    } else if (error.message.includes('BiometryNotAvailable')) {
      throw new Error('Biometrics not available');
    } else if (error.message.includes('BiometryNotEnrolled')) {
      throw new Error('No biometrics enrolled');
    } else {
      throw new Error('Biometric authentication failed');
    }
  }
};

export const storeCredentialsWithBiometrics = async (username, password) => {
  try {
    const biometrics = await checkBiometrics();
    
    if (!biometrics.available) {
      throw new Error('Biometrics not available');
    }

    await Keychain.setInternetCredentials('awscostoptimizer', username, password, {
      accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
      authenticationPrompt: {
        title: 'Store Credentials',
        subtitle: 'Use biometrics to secure your credentials',
        description: 'Your credentials will be encrypted and protected by biometrics',
        cancel: 'Cancel',
      },
    });

    return true;
  } catch (error) {
    console.error('Store credentials with biometrics error:', error);
    throw error;
  }
};

export const getCredentialsWithBiometrics = async () => {
  try {
    const biometrics = await checkBiometrics();
    
    if (!biometrics.available) {
      throw new Error('Biometrics not available');
    }

    const credentials = await Keychain.getInternetCredentials('awscostoptimizer', {
      accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
      authenticationPrompt: {
        title: 'Retrieve Credentials',
        subtitle: 'Use biometrics to access your credentials',
        description: 'Your stored credentials are protected by biometrics',
        cancel: 'Cancel',
      },
    });

    return credentials;
  } catch (error) {
    console.error('Get credentials with biometrics error:', error);
    throw error;
  }
};

export const showBiometricSetupAlert = () => {
  Alert.alert(
    'Biometric Authentication',
    'Set up biometric authentication for secure and convenient access to your AWS Cost Optimizer account.',
    [
      {
        text: 'Not Now',
        style: 'cancel',
      },
      {
        text: 'Set Up',
        onPress: () => {
          // Navigate to biometric setup
          console.log('Navigate to biometric setup');
        },
      },
    ]
  );
};

export const showBiometricErrorAlert = (error) => {
  let title = 'Biometric Authentication Error';
  let message = 'An error occurred during biometric authentication.';

  if (error.message.includes('not available')) {
    title = 'Biometrics Not Available';
    message = 'Biometric authentication is not available on this device.';
  } else if (error.message.includes('not enrolled')) {
    title = 'No Biometrics Enrolled';
    message = 'Please set up biometric authentication in your device settings.';
  } else if (error.message.includes('cancelled')) {
    return; // Don't show alert for user cancellation
  }

  Alert.alert(title, message, [
    {
      text: 'OK',
      style: 'default',
    },
  ]);
};
