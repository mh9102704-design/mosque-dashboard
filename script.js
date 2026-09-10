import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getFirestore, doc, onSnapshot, setDoc } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
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

// 1. Live Sync (Runs immediately so they see times while installing)
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

// 2. Strict iOS Detection & PWA Enforcement
const isIos = () => /iphone|ipad|ipod/.test(window.navigator.userAgent.toLowerCase());
const isStandalone = () => ('standalone' in window.navigator) && (window.navigator.standalone);

// If they are on an iPhone but in the Safari browser, show the instructional overlay
if (isIos() && !isStandalone()) {
    const modal = document.getElementById('ios-install-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Inject strictly Apple-specific visual instructions
    document.querySelector('#ios-install-modal .bg-gray-50').innerHTML = `
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 24px; margin-right: 12px;">📤</span>
            <p class="text-sm m-0">Tap the <strong>Share</strong> icon at the bottom of Safari.</p>
        </div>
        <div style="display: flex; align-items: center;">
            <span style="font-size: 24px; margin-right: 12px;">➕</span>
            <p class="text-sm m-0">Scroll down and tap <strong>Add to Home Screen</strong>.</p>
        </div>
    `;
}

// Ensure they can dismiss the modal if they just want to read the times
document.getElementById('close-modal-btn').addEventListener('click', () => {
    document.getElementById('ios-install-modal').classList.add('hidden');
    document.getElementById('ios-install-modal').classList.remove('flex');
});

// 3. Notification Setup (ONLY triggers in the installed Home Screen app)
const setupNotifications = async () => {
    try {
        const messagingSupported = await isSupported();
        if (!messagingSupported) return;

        const messaging = getMessaging(app);
        const enableBtn = document.getElementById('enable-notifications-btn');
        
        // Only unhide the notification button in the installed app environment
        document.getElementById('notification-section').classList.remove('hidden');

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
                        // Automatically register the user to Firestore
                        await setDoc(doc(db, "subscribers", token), {
                            token: token,
                            timestamp: new Date()
                        });

                        enableBtn.innerText = "✅ Alerts Enabled";
                        enableBtn.classList.replace("bg-blue-600", "bg-emerald-600");
                        enableBtn.disabled = true;
                    }
                } else {
                    alert("Please open your iPhone Settings and allow notifications for this app.");
                }
            } catch (error) {
                console.error("Token error:", error);
            }
        });

        // Handle alerts while actively viewing the app
        onMessage(messaging, (payload) => {
            alert(`Mosque Update: ${payload.notification.title}\n${payload.notification.body}`);
        });
    } catch (err) {
        console.error("Messaging setup failed:", err);
    }
};

// Fire the setup strictly for installed users
if (isStandalone() || (!isIos() && window.matchMedia('(display-mode: standalone)').matches)) {
    setupNotifications();
}
