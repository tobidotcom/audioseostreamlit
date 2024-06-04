import streamlit as st
import os
import shutil
import mutagen
import re
import zipfile
from mutagen.id3 import ID3, TRCK, TALB, TPE2, TDRC, TIT2, TCON
import tempfile
import io

def get_user_metadata():
    st.write("Let's fill in the metadata for your audio files! 🎵")
    metadata = {}

    metadata['album_title'] = st.text_input("What is the album title?", value="Unknown", key="album_title")
    metadata['album_artist'] = st.text_input("Who is the album artist?", value="Unknown", key="album_artist")
    metadata['year'] = st.text_input("What year was the album released? (or press Enter to skip):", key="year")
    if metadata['year']:
        try:
            metadata['year'] = int(metadata['year'])
        except ValueError:
            st.warning(f"Invalid year: '{metadata['year']}'. Setting year to 'Unknown'.")
            metadata['year'] = 'Unknown'
    metadata['genre'] = st.text_input("What is the genre of the album?", value="Unknown", key="genre")

    return metadata

def add_metadata(audio_file, metadata, track_number, temp_dir):
    # Read the bytes from the UploadedFile object
    audio_bytes = audio_file.read()
    
    # Create a BytesIO object with the audio bytes
    audio_io = io.BytesIO(audio_bytes)
    
    # Pass the BytesIO object to mutagen.File
    audio = mutagen.File(audio_io)
    
    if audio.tags is None:
        audio.add_tags()
        audio.tags = ID3()

    audio.tags.add(TALB(encoding=3, text=metadata['album_title']))
    audio.tags.add(TPE2(encoding=3, text=metadata['album_artist']))
    if metadata['year'] != 'Unknown':
        audio.tags.add(TDRC(encoding=3, text=str(metadata['year'])))
    audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    audio.tags.add(TIT2(encoding=3, text=audio_file.name))  # Add title tag
    audio.tags.add(TCON(encoding=3, text=metadata['genre']))  # Add genre tag

    audio.save(audio_io)
    audio_io.seek(0)  # Reset the BytesIO object to the beginning

    # Rename the file with SEO-friendly name
    file_name, file_ext = os.path.splitext(audio_file.name)
    seo_friendly_name = f"{str(track_number).zfill(2)}-{metadata['album_artist'].lower().replace(' ', '-')}-{file_name.lower().replace(' ', '-')}{file_ext}"
    new_file_path = os.path.join(temp_dir, seo_friendly_name)
    with open(new_file_path, 'wb') as f:
        f.write(audio_io.getbuffer())

def main():
    st.title("Audio Metadata Editor")

    metadata = get_user_metadata()

    uploaded_files = st.file_uploader("Choose audio files", accept_multiple_files=True)

    if uploaded_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, file in enumerate(uploaded_files, start=1):
                add_metadata(file, metadata, i, temp_dir)
                st.success(f"Metadata added and file renamed for {file.name}")

            # Create a zip file with the processed files
            zip_file = zipfile.ZipFile("processed_files.zip", "w")
            for file_name in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file_name)
                zip_file.write(file_path, file_name)
            zip_file.close()

            # Provide a download link for the zip file
            with open("processed_files.zip", "rb") as f:
                bytes = f.read()
                st.download_button(
                    label="Download Processed Files",
                    data=bytes,
                    file_name="processed_files.zip",
                    mime="application/zip",
                )

            # Remove the temporary zip file
            os.remove("processed_files.zip")
    else:
        st.warning("Please upload audio files to process.")

if __name__ == "__main__":
    main()
