from PIL import Image, ImageDraw

# Crear un icono simple programáticamente
img = Image.new('RGB', (64, 64), color='#2E86AB')
draw = ImageDraw.Draw(img)
draw.rectangle([16, 16, 48, 48], fill='white')
img.save('icon.ico', format='ICO')