import os
import shutil
import mutagen
from mutagen.id3 import ID3, TRCK, TALB, TIT3, TPE1, TPE2, COMM, TCON, TDRC, TLEN, TBPM, TPUB, TCOP, WOAR, WPUB, TXXX, POPM, TMOO, TIT1
import re
import zipfile
import tempfile

def add_metadata(audio_file, metadata, track_number, temp_dir):
    temp_file_path = os.path.join(temp_dir, audio_file.name)
    shutil.copy2(audio_file.name, temp_file_path)

    audio = mutagen.File(temp_file_path)
    if audio.tags is None:
        audio.add_tags()
        audio.tags = ID3()

    audio.tags.add(TALB(encoding=3, text=metadata['title']))
    if metadata['subtitle']:
        audio.tags.add(TIT3(encoding=3, text=metadata['subtitle']))
    audio.tags.add(POPM(email='rating@example.com', rating=metadata['rating'], count=1))
    if metadata['comments']:
        audio.tags.add(COMM(encoding=3, lang='eng', desc='comment', text=[metadata['comments']]))
    if metadata['contributing_artists']:
        audio.tags.add(TPE1(encoding=3, text=metadata['contributing_artists']))
    audio.tags.add(TPE2(encoding=3, text=metadata['album_artist']))
    if metadata['year']:
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

    audio.save()

    # Rename the file with SEO-friendly name
    if metadata['keywords']:
        keywords = [re.sub(r'[^a-zA-Z0-9\s]', '', keyword.strip().lower()) for keyword in metadata['keywords'].split(',')]
        file_name, file_ext = os.path.splitext(audio_file.name)
        seo_friendly_name = f"{str(track_number).zfill(2)}-{metadata['album_artist'].lower().replace(' ', '-')}-{file_name.lower().replace(' ', '-')}-{'-'.join(keyword for keyword in keywords[:3])[:60]}{file_ext}"
        new_file_path = os.path.join(temp_dir, seo_friendly_name)
        shutil.move(temp_file_path, new_file_path)
    else:
        file_name, file_ext = os.path.splitext(audio_file.name)
        seo_friendly_name = f"{str(track_number).zfill(2)}-{metadata['album_artist'].lower().replace(' ', '-')}-{file_name.lower().replace(' ', '-')}{file_ext}"
        new_file_path = os.path.join(temp_dir, seo_friendly_name)
        shutil.move(temp_file_path, new_file_path)
