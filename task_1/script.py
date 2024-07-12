import argparse
import asyncio
import logging
import os
import shutil

log = logging.getLogger()


async def read_folder(source_folder):
    files_list = []
    r_tasks = []

    try:
        listdir = os.listdir(source_folder)
    except Exception as e:
        log.error(f'Error occurred when reading directory "{source_folder}". {e}')
        return []

    for f in listdir:
        file_path = os.path.join(source_folder, f)
        if os.path.isdir(file_path):
            read = asyncio.create_task(read_folder(file_path))
            r_tasks.append(read)
        else:
            files_list.append(file_path)

    read_folders = await asyncio.gather(*r_tasks)
    [files_list.extend(f) for f in read_folders]

    return files_list


async def copy_file(file_path: str, output):
    try:
        ext = file_path.split('.')[-1]
        dest = os.path.join(output, ext)
        os.makedirs(dest, exist_ok=True)
        shutil.copy2(file_path, dest)
    except Exception as e:
        log.error(f'Error occurred when copying file "{file_path}" to directory "{output}". {e}')


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    source, output = args.source, args.output
    files_list = await read_folder(source)
    cp_tasks = [asyncio.create_task(copy_file(file, output)) for file in files_list]
    await asyncio.gather(*cp_tasks)


if __name__ == '__main__':
    asyncio.run(main())
