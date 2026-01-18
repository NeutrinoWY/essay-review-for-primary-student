import gradio as gr
import os
from utils import convert_heic_to_png
from chat_completions import process_essay


def add_images(new_images, current_images):
    """Add new images to the current list."""
    if current_images is None:
        current_images = []
    if new_images is None:
        return current_images, gr.update(value=current_images), gr.update(choices=[], value=None)
    
    # Handle both single file and list of files
    if not isinstance(new_images, list):
        new_images = [new_images]
    
    # Extract file paths and convert HEIC to PNG if needed
    for img in new_images:
        if isinstance(img, dict):
            img_path = img.get('name') or img.get('path')
        else:
            img_path = img
        
        if img_path:
            # Convert HEIC to PNG for display in gallery, and add the paths to current images
            converted_path = convert_heic_to_png(img_path) if img_path.lower().endswith(('.heic', '.heif')) else img_path
            if converted_path not in current_images:
                current_images.append(converted_path)
    
    # Update dropdown choices
    choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(current_images)]
    return current_images, gr.update(value=current_images), gr.update(choices=choices, value=choices[-1] if choices else None)


def move_image_up(selected_choice, images):
    """Move an image up in the list."""
    if images is None or len(images) == 0:
        return images, gr.update(value=images), gr.update(choices=[], value=None)
    
    index = get_selected_index(selected_choice, images)
    if index <= 0:
        choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(images)]
        return images, gr.update(value=images), gr.update(choices=choices, value=selected_choice)
    
    images = images.copy()
    images[index], images[index - 1] = images[index - 1], images[index]
    choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(images)]
    new_selection = choices[index - 1]  # Update selection to moved position
    return images, gr.update(value=images), gr.update(choices=choices, value=new_selection)


def move_image_down(selected_choice, images):
    """Move an image down in the list."""
    if images is None or len(images) == 0:
        return images, gr.update(value=images), gr.update(choices=[], value=None)
    
    index = get_selected_index(selected_choice, images)
    if index >= len(images) - 1:
        choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(images)]
        return images, gr.update(value=images), gr.update(choices=choices, value=selected_choice)
    
    images = images.copy()
    images[index], images[index + 1] = images[index + 1], images[index]
    choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(images)]
    new_selection = choices[index + 1]  # Update selection to moved position
    return images, gr.update(value=images), gr.update(choices=choices, value=new_selection)


def remove_image(selected_choice, images):
    """Remove an image from the list."""
    if images is None or len(images) == 0:
        return images, gr.update(value=images), gr.update(choices=[], value=None)
    
    index = get_selected_index(selected_choice, images)
    images = images.copy()
    images.pop(index)
    
    if len(images) == 0:
        return images, gr.update(value=None), gr.update(choices=[], value=None)
    
    choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(images)]
    # Select the image at the same index, or the last one if we removed the last item
    new_selection = choices[min(index, len(choices) - 1)] if choices else None
    return images, gr.update(value=images), gr.update(choices=choices, value=new_selection)


def update_gallery_display(images):
    """Update the gallery display based on current image list."""
    if images is None or len(images) == 0:
        return gr.update(value=None), gr.update(choices=[], value=None)
    # Create choices for dropdown showing image order
    choices = [f"Image {i+1}: {os.path.basename(img) if isinstance(img, str) else 'Image'}" for i, img in enumerate(images)]
    return gr.update(value=images), gr.update(choices=choices, value=choices[0] if choices else None)


def get_selected_index(selected_choice, images):
    """Get the index of the selected image from the dropdown."""
    if selected_choice is None or images is None or len(images) == 0:
        return 0
    try:
        # Extract index from choice string "Image X: filename"
        index = int(selected_choice.split(":")[0].split()[-1]) - 1
        return max(0, min(index, len(images) - 1))
    except:
        return 0


# Create Gradio interface
with gr.Blocks(title="Primary Student Essay Reviewer", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 📝 Primary Student Essay Reviewer
        
        Upload multiple essay images, reorder them using the buttons, and AI will recognize the text from all images in order and provide detailed review feedback.
        """
    )
    
    # State to store the ordered list of images
    image_state = gr.State(value=[])
    
    with gr.Row():
        with gr.Column(scale=1):
            file_upload = gr.File(
                label="Upload Essay Images",
                file_count="multiple",
                file_types=["image"],
                height=80
            )
            
            image_gallery = gr.Gallery(
                label="Images (Order matters - use controls below to reorder)",
                type="filepath",
                height=320,
                show_label=False,
                columns=3,
                rows=2,
                allow_preview=True
            )
            
            image_selector = gr.Dropdown(
                label="Select Image to Reorder",
                choices=[],
                value=None,
                interactive=True
            )
            
            with gr.Row():
                move_up_btn = gr.Button("⬆️ move up", size="sm")
                move_down_btn = gr.Button("⬇️ move down", size="sm")
                remove_btn = gr.Button("🗑️ delete", size="sm", variant="stop")
            
            process_btn = gr.Button("Recognize and Analyze", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            recognized_text_output = gr.Textbox(
                label="Recognized Text (Combined from All Images)",
                lines=25,
                placeholder="Recognized essay content from all images will appear here...",
                interactive=True
            )
    
    analysis_output = gr.Markdown(
        label="Analysis Results",
        value="Analysis results will appear here..."
    )
    
    # File upload handler, adding the 'png' converted images to state
    file_upload.upload(
        fn=add_images,
        inputs=[file_upload, image_state],
        outputs=[image_state, image_gallery, image_selector]
    )
    
    # Reordering buttons
    move_up_btn.click(
        fn=move_image_up,
        inputs=[image_selector, image_state],
        outputs=[image_state, image_gallery, image_selector]
    )
    
    move_down_btn.click(
        fn=move_image_down,
        inputs=[image_selector, image_state],
        outputs=[image_state, image_gallery, image_selector]
    )
    
    remove_btn.click(
        fn=remove_image,
        inputs=[image_selector, image_state],
        outputs=[image_state, image_gallery, image_selector]
    )
    
    # Process button click
    process_btn.click(
        fn=process_essay,
        inputs=[image_state],
        outputs=[recognized_text_output, analysis_output]
    )
    

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
