import os
import requests
import cloudinary
from cloudinary.uploader import upload

def change_url(url):
  
    # Download the image
    url = url.strip('\"')
    response = requests.get(url)
    image_filename = "downloaded_image.png"
    
    # Save the image
    with open(image_filename, 'wb') as file:
        file.write(response.content)
    
    # Configure Cloudinary
    cloudinary.config( 
        cloud_name = "ddkew4hpt", 
        api_key = "382326976464937", 
        api_secret = "IGX2Pas1Uctk3kSuci_OdkN3IgY" 
    )

    # Upload the image to Cloudinary
    upload_result = upload(image_filename)
    print(upload_result)
    print(upload_result['secure_url'])
    
    # Remove the local image file
    os.remove(image_filename)
    
    print(f"Cloudinary link: {upload_result['secure_url']}")

    # Return the Cloudinary URL
    return upload_result['secure_url']
