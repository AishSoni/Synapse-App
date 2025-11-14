"""
Generate Synapse extension icons
Run: python generate_icons.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_icon(size):
    """Create an icon with gradient background and 'S' letter"""
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle with gradient effect
    # We'll simulate gradient by drawing multiple rectangles
    for i in range(size):
        # Calculate color for this row (gradient from #667eea to #764ba2)
        r1, g1, b1 = 0x66, 0x7e, 0xea  # Start color
        r2, g2, b2 = 0x76, 0x4b, 0xa2  # End color

        progress = i / size
        r = int(r1 + (r2 - r1) * progress)
        g = int(g1 + (g2 - g1) * progress)
        b = int(b1 + (b2 - b1) * progress)

        draw.line([(0, i), (size, i)], fill=(r, g, b, 255))

    # Make it a rounded square by masking corners
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = int(size * 0.2)
    mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=255)

    # Apply mask
    img.putalpha(mask)

    # Draw 'S' letter
    try:
        # Try to use a nice font
        font_size = int(size * 0.6)
        # Try different font paths
        font_paths = [
            'C:\\Windows\\Fonts\\arialbd.ttf',  # Windows
            '/System/Library/Fonts/Helvetica.ttc',  # Mac
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
        ]

        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, font_size)
                break

        if font is None:
            # Fallback to default font
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Draw text
    text = "S"

    # Get text bounding box to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    return img

# Generate all required sizes
sizes = [16, 32, 48, 128]

for size in sizes:
    icon = create_gradient_icon(size)
    filename = f'icon{size}.png'
    icon.save(filename, 'PNG')
    print(f'[OK] Created {filename}')

print('\n[SUCCESS] All icons generated successfully!')
print('Icons are ready in the current directory.')
