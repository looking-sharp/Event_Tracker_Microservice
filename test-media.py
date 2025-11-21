import requests 

url = "http://localhost:5004/upload"
url2 = "http://localhost:5004/delete"
image_path = "test-image-2.jpg"
url_id = ""

with open(image_path, "rb") as f:
    files = {
        "file": (image_path, f, "image/jpeg")
    }
    response = requests.post(url, files=files)

    try:
        data = response.json()
        url_id = data["url_id"]
        print(data)
    except:
        print (response.text)

response2 = requests.post(f"{url2}/{url_id}")
try:
    data = response2.json()
    print(data)
except:
    print (response2.text)


