import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import instaloader

# Muat variabel lingkungan dari file .env
load_dotenv()

# Inisialisasi Instaloader
L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=True,
    compress_json=False,
    download_video_thumbnails=False,
    save_metadata=False,
    post_metadata_txt_pattern=None
)

def download_reels(url: str) -> str:
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    
    target_folder = "reels"
    os.makedirs(target_folder, exist_ok=True)
    L.download_post(post, target=target_folder)
    
    downloaded_files = os.listdir(target_folder)
    for file_name in downloaded_files:
        if file_name.endswith('.mp4'):
            original_video_path = os.path.join(target_folder, file_name)
            new_video_path = os.path.join(target_folder, f"{shortcode}.mp4")
            os.rename(original_video_path, new_video_path)
            return new_video_path

    raise FileNotFoundError("Video tidak ditemukan setelah diunduh.")

def remove_txt_files(folder: str):
    for file_name in os.listdir(folder):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder, file_name)
            os.remove(file_path)
            print(f"File {file_path} telah dihapus.")

async def reels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Mohon sertakan URL Reels Instagram!")
        return
    
    url = context.args[0]
    video_path = None 

    try:
        video_path = download_reels(url)
        print(f"Video berhasil diunduh: {video_path}") 
        
        with open(video_path, "rb") as video_file:
            await update.message.reply_video(video=video_file)

    except Exception as e:
        print(f"Error: {e}") 

    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
            print(f"Video {video_path} telah dihapus.")
        else:
            print(f"Video {video_path} tidak ditemukan saat mencoba menghapus.")
        
        remove_txt_files("reels")

if __name__ == '__main__':
    TOKEN = os.getenv('TOKEN')  
    if TOKEN is None:
        raise ValueError("Token tidak ditemukan :(")

    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("reels", reels_command))

    print('polling...')
    app.run_polling(poll_interval=3)
