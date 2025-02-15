import asyncio
import aiofiles
import shutil
from pathlib import Path

allowed_extensions = ["png", "jpg", "doc", "docx", "ppt", "pptx", "xls", "xlsx"]

async def create_or_clean_folder(folder_path: Path):
    if folder_path.exists():
        print(f"Очищення папки: {folder_path}")
        for item in folder_path.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"Помилка при видаленні {item}: {e}")
    else:
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"Створено папку: {folder_path}")
        except Exception as e:
            print(f"Помилка при створенні папки {folder_path}: {e}")

async def create_dummy_files(source_path: Path):
    print("Створення dummy файлів...")
    for i in range(1, 101):
        ext = allowed_extensions[(i - 1) % len(allowed_extensions)]
        file_name = f"file_{i}.{ext}"
        file_path = source_path / file_name
        try:
            async with aiofiles.open(file_path, "w") as f:
                await f.write("")
        except Exception as e:
            print(f"Помилка при створенні файлу {file_path}: {e}")
    print("Створення dummy файлів завершено.")

async def read_folder(folder_path: Path):
    print("Початок рекурсивного читання папки...")
    files = []
    try:
        all_items = await asyncio.to_thread(lambda: list(folder_path.rglob("*")))
        for item in all_items:
            if item.is_file():
                files.append(item)
    except Exception as e:
        print(f"Помилка при читанні папки {folder_path}: {e}")
    print(f"Знайдено файлів: {len(files)}")
    return files

async def copy_file(src_file: Path, dest_folder: Path):
    try:
        ext = src_file.suffix.lstrip(".").lower() or "no_extension"
        if ext not in allowed_extensions:
            print(f"Розширення {ext} не підтримується. Файл {src_file} пропущено.")
            return
        target_folder = dest_folder / ext
        target_folder.mkdir(parents=True, exist_ok=True)
        dest_file = target_folder / src_file.name
        await asyncio.to_thread(shutil.copy2, src_file, dest_file)
        print(f"Файл {src_file.name} скопійовано в {target_folder}")
    except Exception as e:
        print(f"Помилка при копіюванні {src_file} до {dest_file}: {e}")

async def main():
    source_path = Path("./source/")
    output_path = Path("./output/")

    await create_or_clean_folder(source_path)
    await create_or_clean_folder(output_path)

    await create_dummy_files(source_path)

    files = await read_folder(source_path)

    tasks = [copy_file(file, output_path) for file in files]
    await asyncio.gather(*tasks)
    print("Операція завершена.")

if __name__ == "__main__":
    asyncio.run(main())
