import requests
from PIL import Image



from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

def pill(image_io):
    im = Image.open(image_io)



def get_upload_able_file(file_path):
    file =  requests.get(file_path, stream=True)
    file = Image.open(file.raw)
    buffer = BytesIO()
    file.save(buffer, format=file.format)
    buff_val = buffer.getvalue()



    pillow_image  =  ContentFile(buff_val, "fhfh.jpg")

    # image_file = InMemoryUploadedFile(file, None, 'foo.jpg', 'image/jpeg', pillow_image.tell, None)



    return pillow_image