from PIL import Image
import os

def remove_checkered_background(file_path):
    print(f"Processing {file_path}...")
    img = Image.open(file_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Checkered pattern often consists of light gray and dark gray pixels
        # Typically around (128, 128, 128) and (192, 192, 192) or (153, 153, 153) etc.
        # We can also detect if R==G==B and they are not too dark or too light (likely background)
        # Or better: just remove anything that isn't the arrow's core color.
        # But a safer bet is to remove the specific shades of the checkered board.
        
        r, g, b, a = item
        
        # Detect gray/white checkered pattern
        # Common checkered shades: (102,102,102), (153,153,153)
        if (abs(r - g) < 5 and abs(g - b) < 5 and abs(r - b) < 5):
             # It's a gray pixel. Most likely background if it's not part of the arrow's neon glow.
             # In the screenshots, the background is a gray/dark-gray checker.
             # We should avoid removing the arrow colors. 
             # Blue arrow has high B, Green has high G, etc.
             
             # If it's very balanced gray, it's likely the background.
             new_data.append((r, g, b, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(file_path, "PNG")
    print(f"Saved {file_path}")

base_dir = "/Users/roger/Desktop/testOpencode_antigravity/dance-game/src/assets/images/arrows"
files = ["arrow_left.png", "arrow_up.png", "arrow_down.png", "arrow_right.png"]

for f in files:
    full_path = os.path.join(base_dir, f)
    if os.path.exists(full_path):
        remove_checkered_background(full_path)
