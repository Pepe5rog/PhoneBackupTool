# -*- coding: utf-8 -*-
import os

from PIL import Image, ImageDraw

SIZE = 256
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Background rounded square
bg_color = (37, 99, 235, 255)  # blue
d.rounded_rectangle([8, 8, SIZE - 8, SIZE - 8], radius=48, fill=bg_color)

# Phone body (white rounded rect, left side)
phone_x0, phone_y0, phone_x1, phone_y1 = 40, 56, 130, 210
d.rounded_rectangle([phone_x0, phone_y0, phone_x1, phone_y1], radius=16, fill=(255, 255, 255, 255))
# Phone screen (inset)
d.rounded_rectangle([phone_x0 + 8, phone_y0 + 14, phone_x1 - 8, phone_y1 - 22], radius=6, fill=bg_color)
# Home button
d.ellipse([phone_x0 + (phone_x1 - phone_x0) // 2 - 6, phone_y1 - 16,
           phone_x0 + (phone_x1 - phone_x0) // 2 + 6, phone_y1 - 4], fill=(255, 255, 255, 255))

# Arrow from phone to folder
arrow_y = 130
d.line([140, arrow_y, 175, arrow_y], fill=(255, 255, 255, 255), width=10)
d.polygon([(175, arrow_y - 14), (200, arrow_y), (175, arrow_y + 14)], fill=(255, 255, 255, 255))

# Folder (bottom right)
fx0, fy0, fx1, fy1 = 150, 150, 226, 210
d.polygon([(fx0, fy0 + 10), (fx0 + 22, fy0 + 10), (fx0 + 30, fy0), (fx1, fy0),
           (fx1, fy1), (fx0, fy1)], fill=(255, 214, 102, 255))
d.rounded_rectangle([fx0, fy0 + 14, fx1, fy1], radius=6, fill=(255, 200, 60, 255))

img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icon saved")
