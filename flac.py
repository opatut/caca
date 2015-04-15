extensions = ['flac']
decode = 'flac -d "{src}" -s > "{target}"'
encode = 'flac -e "{src}" -s > "{target}"'

def direct_convert(target_extension, src, target):
    if target_extension == 'mp3':
        return 'ffmpeg -y -loglevel warning -i "{src}" -qscale:a 0 "{target}"'

