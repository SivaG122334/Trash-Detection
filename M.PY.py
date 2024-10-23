import streamlit as st
from twilio.rest import Client
import folium
from streamlit_folium import st_folium
import geopy.geocoders
from geopy.geocoders import Nominatim

# Twilio credentials
account_sid = 'AC066c96df90833060eb10cfaa8d978deb'
auth_token = '4a4dad8f39684d89709aae3087f67e4d'
client = Client(account_sid, auth_token)

# Function to send WhatsApp message with location link
def send_whatsapp_message(waste_type, lat, lon, additional_message):
    try:
        # Create a Google Maps link for the location
        location_link = f"https://www.google.com/maps?q={lat},{lon}"
        content_message = (
            f"Hey there, a {waste_type} has been placed at Latitude: {lat}, Longitude: {lon}.\n"
            f"Click to view the location: {location_link}\n\n"
            f"Additional message: {additional_message}"
        )
        
        # Send WhatsApp message with location link
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=content_message,
            to='whatsapp:+916282684814'
        )
        return message.sid
    except Exception as e:
        st.error(f"Error sending WhatsApp message: {e}")
        return None

# Initialize reward counter in Streamlit session state
if 'reward_count' not in st.session_state:
    st.session_state['reward_count'] = 0

# Main page function
def waste_message_page():
    st.title("Waste Type Selection and Location Reporting")

    # Display reward count with custom icon
    st.markdown(f"### 🌟 Reward Points: **{st.session_state['reward_count']}**")

    # Dropdown for waste type selection
    waste_type = st.selectbox("Choose Waste Type", ["Hen Waste", "Buffalo Waste"])

    # Input to search for a place (geolocation by name)
    place_name = st.text_input("Search for a place")

    # Initialize map centered on India
    lat, lon = 20.5937, 78.9629
    m = folium.Map(location=[lat, lon], zoom_start=5)

    # Geolocate based on place name (if provided)
    geolocator = Nominatim(user_agent="waste_locator")
    if place_name:
        location = geolocator.geocode(place_name)
        if location:
            lat, lon = location.latitude, location.longitude
            m = folium.Map(location=[lat, lon], zoom_start=12)
            st.success(f"Location found: {place_name} (Lat: {lat}, Lon: {lon})")
        else:
            st.error("Location not found. Try a different name.")

    # Add map marker based on clicked position
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

    if map_data and map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.write(f"Selected Location: Latitude: {lat}, Longitude: {lon}")

    # Additional message box for user input
    additional_message = st.text_area("Add any additional message or details")

    # Button to send message
    if st.button("Send WhatsApp Message"):
        message_sid = send_whatsapp_message(waste_type, lat, lon, additional_message)
        if message_sid:
            st.success(f"WhatsApp message sent successfully! Message SID: {message_sid}")
            st.balloons()
            st.write("🎉 Congratulations! You've successfully reported the waste.")
            # Increment reward counter
            st.session_state['reward_count'] += 5  # Add 5 points as a reward
        else:
            st.error("Failed to send the WhatsApp message.")

# Streamlit app navigation
def main1():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Waste Reporting"])

    if page == "Home":
        st.title("Welcome to the Waste Classification App")
        st.write("Use the app to classify waste and help with proper disposal.")
    elif page == "Waste Reporting":
        waste_message_page()

if __name__ == "__main__":
    main1()


