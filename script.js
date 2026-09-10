import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-messaging.js";

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
const messaging = getMessaging(app);

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

if (isIos() && !isStandalone()) {
    document.getElementById('ios-install-modal').classList.remove('hidden');
    document.getElementById('ios-install-modal').classList.add('flex');
}

document.getElementById('close-modal-btn').addEventListener('click', () => {
    document.getElementById('ios-install-modal').classList.add('hidden');
    document.getElementById('ios-install-modal').classList.remove('flex');
});

if (isStandalone() || !isIos()) {
    document.getElementById('notification-section').classList.remove('hidden');
}

// Button Logic to Request Notification Permissions
const enableBtn = document.getElementById('enable-notifications-btn');
enableBtn.addEventListener('click', async () => {
    // Button Logic to Request Notification Permissions
const enableBtn = document.getElementById('enable-notifications-btn');
enableBtn.addEventListener('click', async () => {
    try {
        // Ask the user for permission
        const permission = await Notification.requestPermission();
        
        if (permission === 'granted') {
            // Explicitly point to the GitHub Pages sub-folder
            const registration = await navigator.serviceWorker.register('/mosque-dashboard/firebase-messaging-sw.js');
            
            // Generate the secure device token
            const token = await getToken(messaging, { 
                vapidKey: "BFiA28041VRV4E9YXRwBqh6t2npCEUCnmQKK9Zfzy7tNNJM-vNonF8hEsnxXf2m985T0Gi-hQDCRqeBQooGK3wk",
                serviceWorkerRegistration: registration
            });
            
            if (token) {
                console.log("Device Token:", token);
                enableBtn.innerText = "✅ Alerts Enabled";
                enableBtn.classList.replace("bg-blue-600", "bg-emerald-600");
                enableBtn.disabled = true;
            }
        } else {
            alert("Permission denied. You can enable notifications in your browser settings.");
        }
    } catch (error) {
        console.error("Error setting up notifications:", error);
        alert("An error occurred. Check your connection and try again.");
    }
});

// Handle incoming alerts if the user is actively looking at the webpage
onMessage(messaging, (payload) => {
    alert(`Mosque Update: ${payload.notification.title}\n${payload.notification.body}`);
});
