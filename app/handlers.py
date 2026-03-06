from aiogram import Router,F
from aiogram.filters import CommandStart,Command
from aiogram.types import Message
from aiogram.types import FSInputFile
router = Router()
import app.keyboards as kb
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f"Привет \n Твой ID{message.from_user.id} "f"\n Твое имя: {message.from_user.first_name}",
                        reply_markup=kb.main)
photo_file = FSInputFile(path=os.path.join(all_media_dir, 'photo.jpg'))




