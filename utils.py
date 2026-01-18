from PIL import Image
import os


def convert_and_resize_image(image_path: str, max_width: int = 1024, max_height: int = 1024, quality: int = 85) -> Image.Image:
    """Convert image to PNG format and resize to reduce file size.
    
    Args:
        image_path: Path to the image file
        max_width: Maximum width in pixels (default 1024)
        max_height: Maximum height in pixels (default 1024)
        quality: JPEG/PNG compression quality (1-100, default 85)
    
    Returns:
        PIL Image object converted to PNG format and resized
    """
    try:
        # Now try to open the image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if needed (for HEIC or PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize image if it's larger than max dimensions
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        return img
        
    except Exception as e:
        print(f"Error converting image {image_path}: {str(e)}")
        raise Exception(f"Failed to open and convert image: {str(e)}")
    


def convert_heic_to_png(image_path: str) -> str:
    """Convert HEIC image to PNG and save it in a temporary directory.
    
    Args:
        image_path: Path to the original image file
        
    Returns:
        Path to the converted PNG file (or original path if already supported format)
    """
    try:
        # Check if it's a HEIC file
        if image_path.lower().endswith(('.heic', '.heif')):
            # Register HEIC support
            try:
                import pillow_heif
                pillow_heif.register_heif_opener()
            except ImportError:
                print("Warning: pillow_heif not installed")
                return image_path
            
            # Create temp directory for converted images
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), 'essay_assistant_images')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Convert HEIC to PNG
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as PNG
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            png_path = os.path.join(temp_dir, f"{base_name}.png")
            img.save(png_path, format='PNG')
            
            print(f"Converted {image_path} to {png_path}")
            return png_path
        else:
            # Return original path if it's already in a supported format
            return image_path
    except Exception as e:
        print(f"Error converting HEIC: {str(e)}")
        return image_path

