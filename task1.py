import asyncio
import aiofiles
import shutil
from pathlib import Path
import logging
import argparse

allowed_extensions = ["png", "jpg", "doc", "docx", "ppt", "pptx", "xls", "xlsx"]

async def create_or_clean_folder(folder_path: Path):
    if folder_path.exists():
        logging.info(f"Очищення папки: {folder_path}")
        for item in folder_path.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                logging.error(f"Помилка при видаленні {item}: {e}")
    else:
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Створено папку: {folder_path}")
        except Exception as e:
            logging.error(f"Помилка при створенні папки {folder_path}: {e}")

async def create_dummy_files(source_path: Path):
    logging.info("Створення dummy файлів...")
    for i in range(1, 101):
        ext = allowed_extensions[(i - 1) % len(allowed_extensions)]
        file_name = f"file_{i}.{ext}"
        file_path = source_path / file_name
        try:
            async with aiofiles.open(file_path, "w") as f:
                await f.write("")
        except Exception as e:
            logging.error(f"Помилка при створенні файлу {file_path}: {e}")
    logging.info("Створення dummy файлів завершено.")

async def read_folder(folder_path: Path):
    logging.info("Початок рекурсивного читання папки...")
    files = []
    try:
        all_items = await asyncio.to_thread(lambda: list(folder_path.rglob("*")))
        for item in all_items:
            if item.is_file():
                files.append(item)
    except Exception as e:
        logging.error(f"Помилка при читанні папки {folder_path}: {e}")
    logging.info(f"Знайдено файлів: {len(files)}")
    return files

async def copy_file(src_file: Path, dest_folder: Path):
    try:
        ext = src_file.suffix.lstrip(".").lower() or "no_extension"
        if ext not in allowed_extensions:
            logging.info(f"Розширення {ext} не підтримується. Файл {src_file} пропущено.")
            return
        target_folder = dest_folder / ext
        target_folder.mkdir(parents=True, exist_ok=True)
        dest_file = target_folder / src_file.name
        await asyncio.to_thread(shutil.copy2, src_file, dest_file)
        logging.info(f"Файл {src_file.name} скопійовано в {target_folder}")
    except Exception as e:
        logging.error(f"Помилка при копіюванні {src_file} до {dest_file}: {e}")

async def main(source_path: Path, output_path: Path):
    await create_or_clean_folder(source_path)
    await create_or_clean_folder(output_path)
    await create_dummy_files(source_path)
    files = await read_folder(source_path)
    tasks = [copy_file(file, output_path) for file in files]
    await asyncio.gather(*tasks)
    logging.info("Операція завершена.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser()

    parser.add_argument("source_path", type=str, help="Шлях до вхідної папки")
    parser.add_argument("output_path", type=str, help="Шлях до вихідної папки")
    args = parser.parse_args()

    source = Path(args.source_path)
    output = Path(args.output_path)
    asyncio.run(main(source, output))
