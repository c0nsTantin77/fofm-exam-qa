// Public app configuration. FoFM uses its own Firebase project, so progress,
// auth, and live presence are fully separated from the original I2DL site.

export interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  messagingSenderId: string;
  appId: string;
  measurementId?: string;
  databaseURL?: string;
}

export const APP_CONFIG: {
  siteId: string;
  firebase: FirebaseConfig;
  feedbackFormUrl: string;
} = {
  siteId: "fofm-exam-qa",
  firebase: {
    apiKey: "AIzaSyDoS-QHVsvecFqJVT2ezI7vIWWqge0txgQ",
    authDomain: "fofm-79893.firebaseapp.com",
    projectId: "fofm-79893",
    storageBucket: "fofm-79893.firebasestorage.app",
    messagingSenderId: "269059832394",
    appId: "1:269059832394:web:00b8963ee3103c9514c4b3",
    measurementId: "G-RBCEYMT4YV",
    // Realtime Database URL — powers the live "online now" banner.
    databaseURL: "https://fofm-79893-default-rtdb.europe-west1.firebasedatabase.app",
  },
  feedbackFormUrl: "",
};
