import asyncio
import logging
import os
import tempfile
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from .config import Config
from .excel_processor import ExcelProcessor
from .woo_updater import WooUpdater


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


setup_logging()
logger = logging.getLogger(__name__)


async def handle_start(message: Message) -> None:
    await message.answer(
        "سلام! فایل اکسل (.xlsx) رو بفرست تا قیمت‌ها رو به‌روزرسانی کنم.\n\n"
        "ستون‌های مورد نیاز: ‘كد كالا’, ‘قيمت فروش  ’ و (اختیاری) ‘مبلغ تخفيف’."
    )


async def handle_excel_file(message: Message) -> None:
    if not message.document or not message.document.file_name.endswith(".xlsx"):
        await message.answer("❌ لطفاً فقط فایل اکسل با پسوند .xlsx ارسال کنید.")
        return

    # احراز هویت ساده بر اساس لیست ادمین‌ها (اختیاری)
    if Config.ADMIN_IDS and message.from_user and message.from_user.id not in Config.ADMIN_IDS:
        await message.answer("❌ شما مجاز به انجام این عملیات نیستید.")
        return

    try:
        file = await message.bot.get_file(message.document.file_id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            await message.bot.download_file(file.file_path, tmp.name)
            temp_path = tmp.name

        processing_msg = await message.answer("در حال پردازش فایل…")

        processor = ExcelProcessor()
        sku_data = processor.process_file(temp_path)

        if not sku_data:
            await processing_msg.edit_text("❌ پردازش فایل با خطا مواجه شد یا داده معتبری یافت نشد.")
            os.unlink(temp_path)
            return

        await processing_msg.edit_text(
            f"✅ فایل پردازش شد. {len(sku_data)} ردیف معتبر یافت شد.\nدر حال به‌روزرسانی قیمت‌ها…"
        )

        updater = WooUpdater()
        result = await updater.update_prices(sku_data)

        report_lines = [
            "✅ به‌روزرسانی به پایان رسید:",
            f"- کل: {result.get('total', 0)}",
            f"- به‌روزرسانی‌شده: {result.get('updated', 0)}",
            f"- خطا: {result.get('errors', 0)}",
            f"- مدت‌زمان: {result.get('duration', 0)} ثانیه",
        ]
        await processing_msg.edit_text("\n".join(report_lines))
    except Exception as exc:
        logger.exception("خطا در پردازش فایل یا به‌روزرسانی قیمت‌ها")
        await message.answer(f"❌ خطا: {exc}")
    finally:
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass


async def main() -> None:
    # اعتبارسنجی متغیرهای محیطی ضروری
    Config.validate()

    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(handle_start, Command(commands=["start"]))
    dp.message.register(handle_excel_file, F.document)

    logger.info("Bot is starting…")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


