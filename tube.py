from pytube import YouTube

url = input("Введите ссыдку: ")
yt = YouTube(url)


yt.streams.first(progressive = True, file_extension='mp4').order_by('resolution').desc().first().download()
