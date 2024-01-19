import streamlit as st
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Initialize the processor and model outside the function
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("yash-412/fn-small-mr")
model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="mr", task="transcribe")

def get_transcription(filename: str):
    # Load audio file
    speech, sr = librosa.load(filename, sr=16000)
    
    # Process audio using the Whisper processor
    input_features = processor(speech, sampling_rate=16000, return_tensors="pt").input_features

    # Generate transcription using the Whisper model
    predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription

def main():
    st.title("Marathi Enhanced-Whisper Transcription")
    st.sidebar.title("File Upload")

    uploaded_file = st.sidebar.file_uploader("Choose an audio file", type=["wav", "mp3"])

    if uploaded_file:
        st.audio(uploaded_file, format="audio/wav")

        if st.button("Get Transcription"):
            try:
                transcription = get_transcription(uploaded_file.name)
                st.success("Transcription:")
                st.write(transcription[0])

            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
