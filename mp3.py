extensions = ['mp3']
decode = 'lame "{src}" "{target}"'
encode = 'lame "{src}" "{target}"'

def direct_convert(target_extension, src, target):
    if target_extension == 'flac':
        return 'ffmpeg -y -loglevel warning -i "{src}" -qscale:a 0 "{target}"'
