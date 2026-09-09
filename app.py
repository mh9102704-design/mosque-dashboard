import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

st.title("🕌 Mosque Prayer Times Panel")

# 1. Passcode Protection
passcode = st.sidebar.text_input("Enter Admin Passcode", type="password")

# Check if the entered passcode matches the secret passcode
if passcode != st.secrets["ADMIN_PASSCODE"]:
    st.warning("Please enter the correct passcode in the sidebar to access the dashboard.")
    st.stop() # Stops the rest of the code from running until password is correct

# 2. Initialize Firebase using Streamlit Secrets (No JSON file needed)
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # Pulls the Firebase credentials from the secure Streamlit cloud
        firebase_secrets = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secrets)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# 3. Reference the database
doc_ref = db.collection("prayer_times").document("current_schedule")

st.write("Update the daily prayer and sunrise times below. Changes will sync immediately.")

# 4. Fetch and update data
current_data = doc_ref.get().to_dict()

if current_data:
    with st.form("update_times_form"):
        st.subheader("Adjust Times (24-Hour Format)")
        
        fajr = st.text_input("Fajr", value=current_data.get("fajr", ""))
        sunrise = st.text_input("Sunrise", value=current_data.get("sunrise", ""))
        zuhr = st.text_input("Zuhr", value=current_data.get("zuhr", ""))
        asr = st.text_input("Asr", value=current_data.get("asr", ""))
        maghrib = st.text_input("Maghrib", value=current_data.get("maghrib", ""))
        isha = st.text_input("Isha", value=current_data.get("isha", ""))
        
        submitted = st.form_submit_button("Save New Times")
        
        if submitted:
            doc_ref.update({
                "fajr": fajr,
                "sunrise": sunrise,
                "zuhr": zuhr,
                "asr": asr,
                "maghrib": maghrib,
                "isha": isha
            })
            st.success("✅ Prayer times successfully updated in the live database!")
else:
    st.error("Could not fetch data. Please check your database rules.")