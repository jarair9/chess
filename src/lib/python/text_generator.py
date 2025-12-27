import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip
import textwrap

def create_text_clip(
    text: str,
    font_path: str,
    fontsize: int,
    color: str,
    stroke_color: str = None,
    stroke_width: int = 0,
    size: tuple[int, int] = None,
    method: str = "caption", # Ignored, kept for compatibility with signature if needed, but we implement 'caption' behavior logic
    align: str = "center",
    interline: int = 4
) -> ImageClip:
    """
    Creates a MoviePy ImageClip with text rendered using Pillow.
    This replaces moviepy.editor.TextClip which relies on ImageMagick.
    
    Args:
        text: The text to render.
        font_path: Path to the .ttf/.otf font file.
        fontsize: Font size.
        color: Text color (e.g. 'white', '#RRGGBB').
        stroke_color: Color of the text outline.
        stroke_width: Width of the text outline.
        size: (width, height) of the image. Height can be None for auto-height.
        align: 'center', 'left', or 'right'.
        interline: Spacing between lines.
        
    Returns:
        A moviepy.editor.ImageClip containing the rendered text.
    """
    
    # 1. Load Font
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except Exception as e:
        print(f"Warning: Could not load font {font_path}, falling back to default. Error: {e}")
        font = ImageFont.load_default()

    # 2. Wrap Text (if width is provided)
    img_width = size[0] if size else 1080 # Default to 1080 if not specified
    
    # Simple estimation for wrapping: average char width
    # Pillow's getlength is better
    lines = []
    if method == "caption" and img_width:
        # We need to wrap text manually since PIL doesn't do it automatically like ImageMagick 'caption:'
        words = text.split(' ')
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            line_width = font.getlength(test_line)
            # Check if this line exceeds width (minus some padding)
            if line_width <= (img_width - 40): # 20px padding on each side
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
    else:
        lines = [text] # No wrapping if not 'caption' or width not set (label mode)

    # 3. Calculate Image Dimensions
    # Calculate height based on lines
    # Ascent/Descent method is more accurate for height
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + interline
    total_text_height = line_height * len(lines)
    
    img_height = size[1] if (size and size[1]) else (total_text_height + 20) # +20 padding

    # 4. Create Image
    # RGBA for transparency
    image = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 5. Draw Text
    y_offset = (img_height - total_text_height) // 2 if (size and size[1]) else 0

    for line in lines:
        line_width = font.getlength(line)
        
        if align == "center":
            x = (img_width - line_width) // 2
        elif align == "right":
            x = img_width - line_width - 20
        else: # left
            x = 20
            
        # Draw stroke if needed
        if stroke_width > 0 and stroke_color:
            draw.text(
                (x, y_offset), 
                line, 
                font=font, 
                fill=stroke_color, 
                stroke_width=stroke_width,
                stroke_fill=stroke_color
            )
            
        # Draw main text
        draw.text(
            (x, y_offset), 
            line, 
            font=font, 
            fill=color
        )
        
        y_offset += line_height

    # 6. Convert to MoviePy ImageClip
    # Convert PIL image to numpy array
    return ImageClip(np.array(image), transparent=True)
