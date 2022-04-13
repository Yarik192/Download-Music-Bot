from pytube import YouTube


def download_from_utube(url):
    try:
        yt_obj = YouTube(url)
        filename = slugify(yt_obj.title)
        path = yt_obj.streams.get_audio_only().download(output_path="music", filename=filename)
        return path.strip()
    except Exception as e:
        print(e)


def slugify(title):
    return " ".join("".join([x if x.isalpha() else " " for x in title]).split())


if __name__ == '__main__':
    ...