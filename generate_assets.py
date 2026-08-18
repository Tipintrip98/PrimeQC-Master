"""
Generates high-resolution branding assets, ICO icon, and banners for PrimeQC.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_app_icon():
    os.makedirs("resources", exist_ok=True)
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark rounded shield background
    draw.rounded_rectangle([8, 8, 248, 248], radius=48, fill="#0f172a", outline="#0284c7", width=6)

    # Cyan gradient ring / checkmark
    draw.ellipse([40, 40, 216, 216], outline="#0ea5e9", width=8)

    # Big "QC" text or checkmark
    # Draw stylized Checkmark
    points = [(75, 130), (115, 170), (185, 90)]
    draw.line(points, fill="#38bdf8", width=16, joint="curve")

    # Draw "PRIME" pill at bottom
    draw.rounded_rectangle([60, 195, 196, 225], radius=10, fill="#0284c7")
    
    # Save PNG
    png_path = "resources/app_icon.png"
    img.save(png_path, "PNG")
    print(f"Created {png_path}")

    # Save ICO with multiple sizes
    ico_path = "resources/app_icon.ico"
    img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Created {ico_path}")


def create_installer_banner():
    # Installer banner (500x120)
    size = (500, 120)
    img = Image.new("RGB", size, "#0f172a")
    draw = ImageDraw.Draw(img)

    # Gradient/accent bar on left
    draw.rectangle([0, 0, 10, 120], fill="#0284c7")
    draw.rectangle([10, 0, 16, 120], fill="#38bdf8")

    # Banner text representation
    draw.rounded_rectangle([30, 25, 470, 95], radius=8, fill="#1e293b", outline="#334155", width=2)

    banner_path = "resources/installer_banner.png"
    img.save(banner_path, "PNG")
    print(f"Created {banner_path}")


if __name__ == "__main__":
    create_app_icon()
    create_installer_banner()
