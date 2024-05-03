import requests

source_file_url = startTrigger.data.exam_file_url


def download_the_source_file(sourceFileURL):
    r = requests.get(sourceFileURL, stream=True)
    localFilePath = f"/tmp/file.pdf"

    if r.status_code == 200:
        with open(localFilePath, "wb") as file:
            for chunk in r:
                file.write(chunk)
        print(f'Downloaded the Source File in "{localFilePath}" file.')
    else:
        requests.raise_for_status()

    return localFilePath


def generate_hash(sourceFilePath):
    import hashlib

    BLOCK_SIZE = 65536
    file_hash = hashlib.sha256()
    with open(sourceFilePath, "rb") as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()


downloaded_file_path = download_the_source_file(source_file_url)
file_hash = generate_hash(downloaded_file_path)
print(f"File Hash: {file_hash}")

return {"file_hash": file_hash}
