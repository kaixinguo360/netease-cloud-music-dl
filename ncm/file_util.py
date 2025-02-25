# -*- coding: utf-8 -*-

from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB, TRCK, error
from PIL import Image


def resize_img(file_path, max_size=(640, 640), quality=90):
    try:
        img = Image.open(file_path)
    except IOError:
        print('Can\'t open image:', file_path)
        return

    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.LANCZOS)
        img = img.convert('RGB')
        img.save(file_path, quality=quality)


def add_metadata_to_song(file_path, cover_path, song, is_program=False):
    # If no ID3 tags in mp3 file
    try:
        audio = MP3(file_path, ID3=ID3)
    except HeaderNotFoundError:
        print('Can\'t sync to MPEG frame, not an validate MP3 file!')
        return

    if audio.tags is None:
        print('No ID3 tag, trying to add one!')
        try:
            audio.add_tags()
            audio.save()
        except error as e:
            print('Error occur when add tags:', str(e))
            return

    # Modify ID3 tags
    id3 = ID3(file_path)
    # Remove old 'APIC' frame
    # Because two 'APIC' may exist together with the different description
    # For more information visit: http://mutagen.readthedocs.io/en/latest/user/id3.html
    if id3.getall('APIC'):
        id3.delall('APIC')
    # add album cover
    id3.add(
        APIC(
            encoding=0,         # 3 is for UTF8, but here we use 0 (LATIN1) for 163, orz~~~
            mime='image/jpeg',  # image/jpeg or image/png
            type=3,             # 3 is for the cover(front) image
            data=open(cover_path, 'rb').read()
        )
    )
    # add artist name
    if is_program:
        art_name = song['dj']['nickname']
    else:
        art_name = song['artists'][0]['name']
    id3.add(
        TPE1(
            encoding=3,
            text=art_name
        )
    )
    # add song name
    id3.add(
        TIT2(
            encoding=3,
            text=song['name']
        )
    )
    # add album name
    if is_program:
        album_name = song['dj']['brand']
    else:
        album_name = song['album']['name']
    id3.add(
        TALB(
            encoding=3,
            text=album_name
        )
    )
    # add track no
    if not is_program:
        id3.add(
            TRCK(
                encoding=3,
                text="%s/%s" % (song['no'], song['album']['size'])
            )
        )
    # programs doesn't have a valid album info.
    id3.save(v2_version=3)
