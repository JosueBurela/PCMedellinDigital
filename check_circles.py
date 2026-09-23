from PIL import Image
for i in range(2, 8):
    fname = f'temp_cedula_media/image{i}.png' if i != 6 else 'temp_cedula_media/image6.jpeg'
    im = Image.open(fname)
    print(f'{fname}: {im.size}, {im.mode}')
