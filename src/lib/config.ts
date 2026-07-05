// Public app configuration. Firebase access is namespaced by siteId in the
// client code, so FoFM progress/presence stays separate from the original I2DL
// site even while using the same Firebase project.

export interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  messagingSenderId: string;
  appId: string;
  databaseURL?: string;
}

export const APP_CONFIG: {
  siteId: string;
  firebase: FirebaseConfig;
  feedbackFormUrl: string;
} = {
  siteId: "fofm-exam-qa",
  firebase: {
    apiKey: "AIzaSyAoT0ncUPEMNT6bCP8iiNCq4m2GrZUuvas",
    authDomain: "i2dl-c79f8.firebaseapp.com",
    projectId: "i2dl-c79f8",
    storageBucket: "i2dl-c79f8.firebasestorage.app",
    messagingSenderId: "556393668021",
    appId: "1:556393668021:web:70ad506d30691180880dfc",
    // Realtime Database URL — powers the live "online now" banner.
    databaseURL: "https://i2dl-c79f8-default-rtdb.europe-west1.firebasedatabase.app",
  },
  feedbackFormUrl: "",
};
