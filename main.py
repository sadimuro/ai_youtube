from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from pytube import YouTube
import config 
import logging
import os

bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands = ['start', 'go'])
async def start(msg:types.Message):
    await msg.answer(f"Здраствуйте {msg.from_user.first_name}")

def downloader(url, type):
    yt = YouTube(url)
    if type == "video":
        yt.streams.filter(progressive = True, file_extension = 'mp4').order_by('resolution').desc().first().download("video", f"{yt.title}.mp4")
        return f"{yt.title}.mp4"
    elif type == "audio":
        yt.streams.filter(only_audio=True).first().download("audio", f"{yt.title}.mp3")
        return f"{yt.title}.mp3"

class DownloadVideo(StatesGroup):
    download = State()

class DownloadAudio(StatesGroup):
    download = State()

@dp.message_handler(commands='video')
async def video(msg:types.Message):
    await msg.answer(f"Отправьте ссылку и я вам его скачаю")
    await DownloadVideo.download.set()

@dp.message_handler(commands='audio')
async def audio(msg:types.Message):
    await msg.answer(f"Отправьте ссылку и я вам скачаю его в mp3")
    await DownloadAudio.download.set()

@dp.message_handler(state=DownloadVideo.download)
async def download_video_state(msg:types.Message, state:FSMContext):
    await msg.answer("Скачиваем видео, ожидайте...")
    title = downloader(msg.text, "video")
    video = open(f'video/{title}', 'rb')
    try:
        await msg.answer("Все скачалось, вот видео")
        await bot.send_video(msg.chat.id, video)
    except Exception as error:
        await msg.answer(f"Произошла ошибка, повторите еще раз. {error}")
    os.remove(f'video/{title}')
    await state.finish()

@dp.message_handler(state=DownloadAudio.download)
async def download_audio_state(msg:types.Message, state:FSMContext):
    await msg.answer("Скачиваем аудио, ожидайте...")
    title = downloader(msg.text, "audio")
    audio = open(f'audio/{title}', 'rb')
    try:
        await msg.answer("Все скачалось, вот аудио")
        await bot.send_audio(msg.chat.id, audio)
    except Exception as error:
        await msg.answer(f"Произошла ошибка, повторите еще раз. {error}")
    os.remove(f'audio/{title}')
    await state.finish()

executor.start_polling(dp)