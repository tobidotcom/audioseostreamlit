import streamlit as st
import os
import shutil
import mutagen
import re
import zipfile
from mutagen.id3 import ID3, TRCK, TALB, TIT3, TPE1, TPE2, COMM, TCON, TDRC, TLEN, TBPM, TPUB, TCOP, WOAR, WPUB, TXXX, POPM
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
    audio_bytes = audio_file.read() 
    audio_io = io.BytesIO(audio_bytes) 
    audio = mutagen.File(audio_io)

    # Create ID3 tag if it doesn't exist
    if not audio:
        audio = mutagen.id3.ID3()

    # Replace all tags to avoid duplications
    audio.delete()

    audio.add(TALB(encoding=3, text=metadata['title'])) 
    audio.add(TIT3(encoding=3, text=metadata['subtitle'])) 
    audio.add(POPM(email='rating@example.com', rating=metadata['rating'], count=1)) 
    audio.add(COMM(encoding=3, lang='eng', desc='comment', text=metadata['comments'])) 
    audio.add(TPE1(encoding=3, text=metadata['contributing_artists'])) 
    audio.add(TPE2(encoding=3, text=metadata['album_artist'])) 
    audio.add(TDRC(encoding=3, text=str(metadata['year']))) 
    audio.add(TRCK(encoding=3, text=str(track_number))) 
    audio.add(TCON(encoding=3, text=metadata['genre'])) 
    audio.add(TPUB(encoding=3, text=metadata['publisher'])) 
    audio.add(TCOP(encoding=3, text=metadata['copyright'])) 
    audio.add(WOAR(encoding=3, text=metadata['author_url'])) 
    audio.add(WPUB(encoding=3, text=metadata['website_publisher'])) 
    audio.add(TXXX(encoding=3, desc='Composers', text=metadata['composers'])) 
    audio.add(TXXX(encoding=3, desc='Conductors', text=metadata['conductors'])) 
    audio.add(TXXX(encoding=3, desc='Group Description', text=metadata['group_description'])) 
    audio.add(TXXX(encoding=3, desc='Mood', text=metadata['mood'])) 
    audio.add(TXXX(encoding=3, desc='Part of a Set', text=metadata['part_of_set'])) 
    audio.add(TXXX(encoding=3, desc='Original Key', text=metadata['original_key'])) 
    audio.add(TXXX(encoding=3, desc='Protected', text=metadata['protected'])) 

    # Upgrade to v2.3 to make it compatible for windows
    audio.update_to_v23()

    # Save the file with changes
    audio.save(audio_io)
    audio_io.seek(0)

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
