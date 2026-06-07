// App configuration (safe to be public — security is enforced by Firestore rules).
window.APP_CONFIG = {
  firebase: {
    apiKey: "AIzaSyAoT0ncUPEMNT6bCP8iiNCq4m2GrZUuvas",
    authDomain: "i2dl-c79f8.firebaseapp.com",
    projectId: "i2dl-c79f8",
    storageBucket: "i2dl-c79f8.firebasestorage.app",
    messagingSenderId: "556393668021",
    appId: "1:556393668021:web:70ad506d30691180880dfc",
    // Realtime Database URL — needed for the live "online now" banner.
    // Paste the URL shown at the top of the Realtime Database page in the
    // Firebase console (looks like https://i2dl-c79f8-default-rtdb.<region>.firebasedatabase.app
    // or https://i2dl-c79f8-default-rtdb.firebaseio.com). Leave "" to disable the banner.
    databaseURL: "https://i2dl-c79f8-default-rtdb.europe-west1.firebasedatabase.app"
  },
  // Google Form "embed" URL (Send → <> → copy the iframe src)
  feedbackFormUrl: "https://docs.google.com/forms/d/e/1FAIpQLSdmu4CYVZkC1PczoYpyDDUbVNmuRYJuUQnzI4bEGAGYI_UhWQ/viewform?embedded=true"
};
