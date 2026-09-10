import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
import { getMessaging, getToken, onMessage, isSupported } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-messaging.js";

const firebaseConfig = {
  apiKey: "AIzaSyA97omfdQj62cjtgNg51uji7pjXNMkh1aA",
  authDomain: "mosqueclocksystem.firebaseapp.com",
  projectId: "mosqueclocksystem",
  storageBucket: "mosqueclocksystem.firebasestorage.app",
  messagingSenderId: "868033914800",
  appId: "1:868033914800:web:6229b57b9c75bc7f101875"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// 1. Live Sync
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

// 2. Universal PWA Installation Flow
const isIos = () => /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
const isStandalone = () => ('standalone' in window.navigator) && (window.navigator.standalone) || window.matchMedia('(display-mode: standalone)').matches;

// If they are NOT opening this from their home screen, force the install modal
if (!isStandalone()) {
    const modal = document.getElementById('ios-install-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Dynamically swap the text if they are on Android
    if (!isIos()) {
        document.querySelector('#ios-install-modal p.text-gray-600').innerText = "To receive prayer alerts reliably, you must install this app to your Home Screen.";
        document.querySelector('#ios-install-modal .bg-gray-50').innerHTML = '<p class="mb-2 text-sm">1. Tap the <strong>three dots (⋮)</strong> in the top right of Chrome.</p><p class="text-sm">2. Tap <strong>Add to Home screen</strong>.</p>';
    }
}

document.getElementById('close-modal-btn').addEventListener('click', () => {
    document.getElementById('ios-install-modal').classList.add('hidden');
    document.getElementById('ios-install-modal').classList.remove('flex');
});

// Only show the Notification button IF they are using the installed Home Screen app
if (isStandalone()) {
    document.getElementById('notification-section').classList.remove('hidden');
}

// 3. Push Notifications
const setupNotifications = async () => {
    try {
        const messagingSupported = await isSupported();
        if (!messagingSupported) return;

        const messaging = getMessaging(app);
        const enableBtn = document.getElementById('enable-notifications-btn');
        
        enableBtn.addEventListener('click', async () => {
            try {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    const swPath = window.location.pathname.includes('mosque-dashboard') 
                        ? '/mosque-dashboard/firebase-messaging-sw.js' 
                        : './firebase-messaging-sw.js';
                        
                    const registration = await navigator.serviceWorker.register(swPath);
                    const token = await getToken(messaging, { 
                        vapidKey: "BFiA28041VRV4E9YXRwBqh6t2npCEUCnmQKK9Zfzy7tNNJM-vNonF8hEsnxXf2m985T0Gi-hQDCRqeBQooGK3wk",
                        serviceWorkerRegistration: registration
                    });
                    
                    if (token) {
                        enableBtn.innerText = "✅ Alerts Enabled";
                        enableBtn.classList.replace("bg-blue-600", "bg-emerald-600");
                        enableBtn.disabled = true;
                    }
                } else {
                    alert("Please enable notifications in your phone's app settings.");
                }
            } catch (error) {
                console.error("Token error:", error);
            }
        });

        onMessage(messaging, (payload) => {
            alert(`Mosque Update: ${payload.notification.title}\n${payload.notification.body}`);
        });
    } catch (err) {
        console.error("Messaging setup failed:", err);
    }
};

if (isStandalone()) {
    setupNotifications();
}
