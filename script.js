import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getFirestore, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
import { getMessaging, getToken, onMessage, isSupported } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-messaging.js";

// Your exact Firebase web configuration
const firebaseConfig = {
  apiKey: "AIzaSyA97omfdQj62cjtgNg51uji7pjXNMkh1aA",
  authDomain: "mosqueclocksystem.firebaseapp.com",
  projectId: "mosqueclocksystem",
  storageBucket: "mosqueclocksystem.firebasestorage.app",
  messagingSenderId: "868033914800",
  appId: "1:868033914800:web:6229b57b9c75bc7f101875"
};

// 1. Initialize Core App & Database First (Guarantees times will load)
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

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

// 2. iOS PWA & Device Detection Logic
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

// 3. Push Notifications (Wrapped safely to prevent crashing the times)
const setupNotifications = async () => {
    try {
        // Check if the browser actually supports Firebase Messaging first
        const messagingSupported = await isSupported();
        if (!messagingSupported) {
            console.warn("This browser does not support Firebase Cloud Messaging.");
            return;
        }

        const messaging = getMessaging(app);
        const enableBtn = document.getElementById('enable-notifications-btn');
        
        enableBtn.addEventListener('click', async () => {
            try {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    // Dynamically set the Service Worker path to avoid 404 folder errors
                    const swPath = window.location.pathname.includes('mosque-dashboard') 
                        ? '/mosque-dashboard/firebase-messaging-sw.js' 
                        : './firebase-messaging-sw.js';
                        
                    const registration = await navigator.serviceWorker.register(swPath);
                    
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
                    alert("Notification permission denied. You can enable it in your browser settings.");
                }
            } catch (error) {
                console.error("Token error:", error);
                alert("Could not enable notifications. Try reloading the page.");
            }
        });

        onMessage(messaging, (payload) => {
            alert(`Mosque Update: ${payload.notification.title}\n${payload.notification.body}`);
        });
        
    } catch (err) {
        console.error("Messaging setup failed:", err);
    }
};

// Boot the notification system quietly in the background
setupNotifications();
