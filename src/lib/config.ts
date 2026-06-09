// Public app configuration — safe to ship (Firestore/RTDB security is enforced
// by server-side rules, not by hiding these values). Mirrors the old
// assets/config.js window.APP_CONFIG.

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
  firebase: FirebaseConfig;
  feedbackFormUrl: string;
} = {
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
  // Google Form "embed" URL (Send -> <> -> copy the iframe src).
  feedbackFormUrl:
    "https://docs.google.com/forms/d/e/1FAIpQLSdmu4CYVZkC1PczoYpyDDUbVNmuRYJuUQnzI4bEGAGYI_UhWQ/viewform?embedded=true",
};
