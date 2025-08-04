from PIL import Image
from pathlib import Path
import multiprocessing

def reduce_image_size(file_path: Path, max_file_size: int) -> None:
    """
    Reduces the size of an image file while maintaining its aspect ratio until it is within the specified maximum file size.
    """
    try:
        with Image.open(file_path) as img:
            quality = 95
            while True:
                temp_path = file_path.with_suffix(".temp.jpg")
                img.save(temp_path, 'JPEG', quality=quality)

                if temp_path.stat().st_size <= max_file_size:
                    temp_path.replace(file_path)  # Replace original with reduced-size file
                    break
                else:
                    quality -= 5
                    if quality < 10:
                        temp_path.unlink(missing_ok=True)  # Remove temporary file
                        raise Exception("Could not reduce image size within the specified limit.")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def resize_images_in_dir(directory: Path, max_file_size: int) -> None:
    """
    Resizes all .jpg images in the given directory while displaying a progress bar.
    """
    if not directory.exists() or not directory.is_dir():
        print(f"The specified directory does not exist: {directory}")
        return

    img_files = list(directory.glob('*.jpg'))

    with multiprocessing.Pool() as pool:
        pool.starmap(resize_image, [(img, max_file_size) for img in img_files])

def resize_image(file_path: Path, max_file_size: int) -> None:
    """
    Wrapper function to call reduce_image_size with arguments.
    """
    try:
        reduce_image_size(file_path, max_file_size)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    directory = Path('data/images')  
    max_file_size = 500 * 1024  # Maximum file size in bytes (e.g., 500 KB)

    if not directory.exists():
        print(f"The specified directory does not exist: {directory}")   
        exit(1)

    multiprocessing.freeze_support()
    resize_images_in_dir(directory, max_file_size)
