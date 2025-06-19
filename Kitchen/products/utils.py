import cloudinary
import cloudinary.uploader
import os

# Configure Cloudinary using settings or environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True  # Ensures the secure URL is used
)

def upload(image_file):
    """
    Uploads an image file to Cloudinary and returns the response.
    """
    try:
        # Perform the upload and return the response
        response = cloudinary.uploader.upload(image_file)
        return response  # Return the response, which contains image details including URL
    except Exception as e:
        raise Exception(f"Error uploading image: {e}")

def destroy(public_id):
    """
    Deletes an image from Cloudinary based on the public ID.
    """
    try:
        # Perform the delete operation
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        raise Exception(f"Error deleting image: {e}")
