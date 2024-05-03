import datetime
import os
import time

import requests

# exam file
source_file_url = startTrigger.data.exam_file_url
# answer file
answer_file_url = startTrigger.data.answer_file_url


# API key and base URL for PDF.co Web API
API_KEY = "pdf_co_api_key"
BASE_URL = "https://api.pdf.co/v1"

# Conversion settings
Pages = ""
Password = ""
Async = True


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


def convertPdfToImage(uploadedFileUrl):
    """Converts PDF To Image using PDF.co Web API"""
    image_urls = []
    parameters = {
        "async": Async,
        "password": Password,
        "pages": Pages,
        "url": uploadedFileUrl,
    }
    url = f"{BASE_URL}/pdf/convert/to/jpg"
    response = requests.post(url, data=parameters, headers={"x-api-key": API_KEY})
    if response.status_code == 200:
        json = response.json()
        if not json["error"]:
            jobId = json["jobId"]
            resultFilePlaceholder = json["url"]
            while True:
                status = checkJobStatus(jobId)
                print(datetime.datetime.now().strftime("%H:%M.%S") + ": " + status)
                if status == "success":
                    resJsonImgFiles = requests.get(resultFilePlaceholder)
                    for resultFileUrl in resJsonImgFiles.json():
                        image_urls.append(resultFileUrl)
                    return image_urls
                elif status == "working":
                    time.sleep(3)
                else:
                    raise Exception(status)
        else:
            raise Exception(json["message"])
    else:
        raise requests.HTTPError(
            f"Request error: {response.status_code} {response.reason}"
        )


def checkJobStatus(jobId):
    """Checks server job status"""
    url = f"{BASE_URL}/job/check?jobid={jobId}"
    response = requests.get(url, headers={"x-api-key": API_KEY})
    if response.status_code == 200:
        return response.json()["status"]
    else:
        raise requests.HTTPError(
            f"Request error: {response.status_code} {response.reason}"
        )


def uploadFile(fileName):
    """Uploads file to the cloud"""
    url = f"{BASE_URL}/file/upload/get-presigned-url?contenttype=application/octet-stream&name={os.path.basename(fileName)}"
    response = requests.get(url, headers={"x-api-key": API_KEY})
    if response.status_code == 200:
        json = response.json()
        if not json["error"]:
            uploadUrl = json["presignedUrl"]
            uploadedFileUrl = json["url"]
            with open(fileName, "rb") as file:
                requests.put(
                    uploadUrl,
                    data=file,
                    headers={
                        "x-api-key": API_KEY,
                        "content-type": "application/octet-stream",
                    },
                )
            return uploadedFileUrl
        else:
            raise Exception(json["message"])
    else:
        raise requests.HTTPError(
            f"Request error: {response.status_code} {response.reason}"
        )


# Only split PDF or TIFF files, return original file URL otherwise i.e. we don't need to split images, etc.
if not source_file_url.lower().endswith((".pdf", ".tiff", ".tif")):
    image_urls = [source_file_url]
else:
    # download the file
    downloaded_file_path = download_the_source_file(source_file_url)

    # Upload and convert the file
    uploaded_file_url = uploadFile(downloaded_file_path)
    image_urls = convertPdfToImage(uploaded_file_url)

if not answer_file_url:
    answer_image_urls = []
elif not answer_file_url.lower().endswith((".pdf", ".tiff", ".tif")):
    answer_image_urls = [answer_file_url]
else:
    # download the file
    downloaded_file_path = download_the_source_file(answer_file_url)

    # Upload and convert the file
    uploaded_file_url = uploadFile(downloaded_file_path)
    answer_image_urls = convertPdfToImage(uploaded_file_url)

# Return the results
return {"image_urls": image_urls, "answer_image_urls": answer_image_urls}
