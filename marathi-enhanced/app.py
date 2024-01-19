import streamlit as st
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperConfig

# Initialize the processor and model outside the function
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
config_path = "yash-412/fn-small-mr/final_model"  # Specify the path to your config.json file
config = WhisperConfig.from_pretrained(config_path)
model = WhisperForConditionalGeneration.from_pretrained("yash-412/fn-small-mr")
model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="mr", task="transcribe")

def get_transcription(speech):
    # Process audio using the Whisper processor
    input_features = processor(speech, sampling_rate=16000, return_tensors="pt").input_features

    # Generate transcription using the Whisper model
    predicted_ids = model.generate(input_features)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription

def main():
    st.title("Marathi Enhanced-Whisper Transcription")
    st.write("Upload an audio file")

    uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])

    if uploaded_file:
        st.audio(uploaded_file, format='audio/wav', start_time=0)

        audio_bytes = uploaded_file.read()
        speech, _ = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        if st.button("Transcribe"):
            transcription = get_transcription(speech)
            st.subheader("Transcription:")
            st.write(transcription)

if __name__ == "__main__":
    main()