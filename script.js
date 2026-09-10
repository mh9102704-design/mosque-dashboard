import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";

// Your exact Firebase web configuration
const firebaseConfig = {
  apiKey: "AIzaSyA97omfdQj62cjtgNg51uji7pjXNMkh1aA",
  authDomain: "mosqueclocksystem.firebaseapp.com",
  projectId: "mosqueclocksystem",
  storageBucket: "mosqueclocksystem.firebasestorage.app",
  messagingSenderId: "868033914800",
  appId: "1:868033914800:web:6229b57b9c75bc7f101875"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Listen for real-time updates from Firestore
const docRef = doc(db, "prayer_times", "current_schedule");

onSnapshot(docRef, (docSnap) => {
    if (docSnap.exists()) {
        const data = docSnap.data();
        document.getElementById('fajr').innerText = data.fajr || '--:--';
        document.getElementById('sunrise').innerText = data.sunrise || '--:--';
        document.getElementById('zuhr').innerText = data.zuhr || '--:--';
        document.getElementById('asr').innerText = data.asr || '--:--';
        document.getElementById('maghrib').innerText = data.maghrib || '--:--';
        document.getElementById('isha').innerText = data.isha || '--:--';
    }
});

// iOS PWA & Notification Detection Logic
const isIos = () => {
  const userAgent = window.navigator.userAgent.toLowerCase();
  return /iphone|ipad|ipod/.test(userAgent);
};

const isStandalone = () => {
  return ('standalone' in window.navigator) && (window.navigator.standalone) || window.matchMedia('(display-mode: standalone)').matches;
};

// Show iOS installation modal if on Safari mobile and not added to home screen
if (isIos() && !isStandalone()) {
    document.getElementById('ios-install-modal').classList.remove('hidden');
    document.getElementById('ios-install-modal').classList.add('flex');
}

// Close modal button listener
document.getElementById('close-modal-btn').addEventListener('click', () => {
    document.getElementById('ios-install-modal').classList.add('hidden');
    document.getElementById('ios-install-modal').classList.remove('flex');
});

// Show "Enable Notifications" button for Android or installed PWA
if (isStandalone() || !isIos()) {
    document.getElementById('notification-section').classList.remove('hidden');
}