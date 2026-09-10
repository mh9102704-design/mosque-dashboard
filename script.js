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

// 1. Initialize Core App & Database
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

// 3. Push Notifications with Frictionless UX
const setupNotifications = async () => {
    try {
        const messagingSupported = await isSupported();
        if (!messagingSupported) return;

        const messaging = getMessaging(app);
        const enableBtn = document.getElementById('enable-notifications-btn');
        
        // Helper function for smooth error UI
        const showFrictionlessError = () => {
            enableBtn.innerText = "🔒 Action Required";
            enableBtn.classList.replace("bg-blue-600", "bg-orange-600");
            
            let helpText = document.getElementById('perm-help');
            if (!helpText) {
                helpText = document.createElement('div');
                helpText.id = 'perm-help';
                helpText.className = "text-sm text-gray-700 mt-3 p-3 bg-orange-50 border border-orange-200 rounded-lg text-left shadow-sm";
                helpText.innerHTML = "<strong>Notifications are blocked by your browser.</strong><br><br>1. Tap the 🔒 <strong>lock icon</strong> in the address bar at the top of your screen.<br>2. Tap <strong>Permissions</strong>.<br>3. Switch Notifications to <strong>Allow</strong>.<br>4. Reload this page.";
                enableBtn.parentNode.appendChild(helpText);
            }
        };
        
        enableBtn.addEventListener('click', async () => {
            try {
                // If already denied, show instructions instantly
                if (Notification.permission === 'denied') {
                    showFrictionlessError();
                    return;
                }

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
                        enableBtn.classList.replace("bg-orange-600", "bg-emerald-600");
                        enableBtn.disabled = true;
                        
                        const helpText = document.getElementById('perm-help');
                        if(helpText) helpText.remove();
                    }
                } else {
                    showFrictionlessError();
                }
            } catch (error) {
                console.error("Token error:", error);
            }
        });

        // Display alerts silently if user is actively on the app
        onMessage(messaging, (payload) => {
             // Optional: You can replace this with a Tailwind banner later instead of an alert
             alert(`Mosque Update: ${payload.notification.title}\n${payload.notification.body}`);
        });
        
    } catch (err) {
        console.error("Messaging setup failed:", err);
    }
};

setupNotifications();
