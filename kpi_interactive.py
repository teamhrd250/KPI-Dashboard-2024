import streamlit as st
import speech_recognition as sr
import openai
import pyttsx3
import pandas as pd

# Set up OpenAI API key
openai.api_key = 'YOUR-API-KEY-HERE'  # Replace with your OpenAI API key

# Initialize pyttsx3 engine for audio
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust the speed of speech
engine.setProperty('volume', 1)  # Set volume level to maximum

# Load the Excel file containing KPI data
data_kpi = pd.read_excel("Data KPI Deviasi.xlsx")  # Replace with actual file path or GitHub URL

# Function to generate audio file
def generate_audio(text):
    audio_file_path = '/mnt/data/kpi_narration.mp3'  # Save the file in Streamlit's accessible folder
    engine.save_to_file(text, audio_file_path)
    engine.runAndWait()
    return audio_file_path

# Streamlit Title
st.title("Interactive Voice Assistant with KPI Dashboard")

# Create a button to start voice recognition
if st.button("Start Listening"):
    recognizer = sr.Recognizer()

    # Use microphone to listen for user input
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    # Try recognizing the speech
    try:
        user_input = recognizer.recognize_google(audio)
        st.write(f"You said: {user_input}")
        
        # Get response from ChatGPT API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Model choice
            prompt=user_input,
            max_tokens=150
        )
        
        # Get the response text
        gpt_response = response.choices[0].text.strip()
        
        # Display the GPT response in Streamlit
        st.write(f"ChatGPT's answer: {gpt_response}")
        
        # Check if the user asked about Core Player (for demonstration)
        if "core player" in user_input.lower():
            # Filter the Core Players from the data
            core_players = data_kpi[data_kpi['Nine Box Category'] == 'Core Player']['Nama']
            
            # Show the Core Players in Streamlit
            st.write("Core Players:")
            st.write(core_players.tolist())  # Display names as a list
            
            # Generate the audio for the response
            audio_file_path = generate_audio(f"Core Players are: {', '.join(core_players.tolist())}.")
            
            # Play the audio in Streamlit
            st.audio(audio_file_path, format='audio/mp3')
        
        else:
            # Generate the audio for the general GPT response
            audio_file_path = generate_audio(gpt_response)
            
            # Play the audio in Streamlit
            st.audio(audio_file_path, format='audio/mp3')
    
    except Exception as e:
        st.write("Sorry, I could not understand your request.")
        st.write(f"Error: {e}")
