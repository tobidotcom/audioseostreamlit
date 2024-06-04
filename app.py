import streamlit as st
import os
import shutil
import mutagen
import re
import zipfile
from mutagen.id3 import ID3, TRCK, TALB, TIT3, TPE1, TPE2, COMM, TCON, TDRC, TLEN, TBPM, TPUB, TCOP, WOAR, WPUB, TXXX, POPM, TMOO, TIT1
import tempfile
import io

def get_user_metadata():
    st.write("Let's fill in the metadata for your audio files! 🎵")
    metadata = {}

    metadata['title'] = st.text_input("What is the album title?", value="Unknown", key="title")
    metadata['subtitle'] = st.text_input(f"Enter the subtitle for '{metadata['title']}' (or press Enter to skip):", key="subtitle")
    metadata['rating'] = st.slider("Rate the album (1-5 stars):", 1, 5, 5, key="rating")
    metadata['comments'] = st.text_input("Enter any comments (or press Enter to skip):", key="comments")
    metadata['contributing_artists'] = st.text_input("Enter the contributing artists (or press Enter to skip):", key="contributing_artists")
    metadata['album_artist'] = st.text_input("Who is the album artist?", value="Unknown", key="album_artist")
    metadata['year'] = st.text_input("What year was the album released? (or press Enter to skip):", key="year")
    if metadata['year']:
        try:
            metadata['year'] = int(metadata['year'])
        except ValueError:
            st.warning(f"Invalid year: '{metadata['year']}'. Setting year to 'Unknown'.")
            metadata['year'] = 'Unknown'
    metadata['genre'] = st.text_input("What is the genre of the album? (or press Enter to skip):", key="genre")
    metadata['publisher'] = st.text_input("Who is the publisher? (or press Enter to skip):", key="publisher")
    metadata['copyright'] = st.text_input("Enter the copyright information (or press Enter to skip):", key="copyright")
    metadata['author_url'] = st.text_input("Enter the author's website (or press Enter to skip):", key="author_url")
    metadata['website_publisher'] = st.text_input("Enter the publisher's website (or press Enter to skip):", key="website_publisher")
    metadata['composers'] = st.text_input("Enter the composers (or press Enter to skip):", key="composers")
    metadata['conductors'] = st.text_input("Enter the conductors (or press Enter to skip):", key="conductors")
    metadata['group_description'] = st.text_input("Enter the group description (or press Enter to skip):", key="group_description")
    metadata['mood'] = st.text_input("Enter the mood (or press Enter to skip):", key="mood")
    metadata['part_of_set'] = st.text_input("Enter the part of set (or press Enter to skip):", key="part_of_set")
    metadata['original_key'] = st.text_input("Enter the original key (or press Enter to skip):", key="original_key")
    metadata['protected'] = st.text_input("Is the file protected? (True/False) (or press Enter to skip):", key="protected")
    metadata['keywords'] = st.text_input("Enter three keywords separated by commas (e.g., keyword1, keyword2, keyword3):", key="keywords")

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

    audio.tags.add(TALB(encoding=3, text=metadata['title']))
    if metadata['subtitle']:
        audio.tags.add(TIT3(encoding=3, text=metadata['subtitle']))
    audio.tags.add(POPM(email='rating@example.com', rating=metadata['rating'], count=1))
    if metadata['comments']:
        audio.tags.add(COMM(encoding=3, lang='eng', desc='comment', text=metadata['comments']))
    if metadata['contributing_artists']:
        audio.tags.add(TPE1(encoding=3, text=metadata['contributing_artists']))
    audio.tags.add(TPE2(encoding=3, text=metadata['album_artist']))
    if metadata['year'] != 'Unknown':
        audio.tags.add(TDRC(encoding=3, text=str(metadata['year'])))
    audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    if metadata['genre']:
        audio.tags.add(TCON(encoding=3, text=metadata['genre']))
    if metadata['publisher']:
        audio.tags.add(TPUB(encoding=3, text=metadata['publisher']))
    if metadata['copyright']:
        audio.tags.add(TCOP(encoding=3, text=metadata['copyright']))
    if metadata['author_url']:
        audio.tags.add(WOAR(encoding=3, text=metadata['author_url']))
    if metadata['website_publisher']:
        audio.tags.add(WPUB(encoding=3, text=metadata['website_publisher']))
    if metadata['composers']:
        audio.tags.add(TXXX(encoding=3, desc='Composers', text=metadata['composers']))
    if metadata['conductors']:
        audio.tags.add(TXXX(encoding=3, desc='Conductors', text=metadata['conductors']))
    if metadata['group_description']:
        audio.tags.add(TIT1(encoding=3, text=metadata['group_description']))
    if metadata['mood']:
        audio.tags.add(TMOO(encoding=3, text=metadata['mood']))
    if metadata['part_of_set']:
        audio.tags.add(TXXX(encoding=3, desc='Part of a Set', text=metadata['part_of_set']))
    if metadata['original_key']:
        audio.tags.add(TXXX(encoding=3, desc='Original Key', text=metadata['original_key']))
    if metadata['protected']:
        audio.tags.add(TXXX(encoding=3, desc='Protected', text=metadata['protected']))

    audio.save(audio_io)
    audio_io.seek(0)  # Reset the BytesIO object to the beginning

    # Rename the file with SEO-friendly name
    if metadata['keywords']:
        keywords = [re.sub(r'[^a-zA-Z0-9\s]', '', keyword.strip().lower()) for keyword in metadata['keywords'].split(',')]
        file_name, file_ext = os.path.splitext(audio_file.name)
        seo_friendly_name = f"{str(track_number).zfill(2)}-{metadata['album_artist'].lower().replace(' ', '-')}-{file_name.lower().replace(' ', '-')}-{'-'.join(keyword for keyword in keywords[:3])[:60]}{file_ext}"
        new_file_path = os.path.join(temp_dir, seo_friendly_name)
        with open(new_file_path, 'wb') as f:
            f.write(audio_io.getbuffer())
    else:
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
