import zipfile, os
from PIL import Image

docx_path = r'C:\Users\burel\Downloads\CEDULA DE EVALUACION SIMU MEDELLIN.docx'
out_dir = 'temp_cedula_media'
os.makedirs(out_dir, exist_ok=True)

with zipfile.ZipFile(docx_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('word/media/'):
            fname = os.path.basename(name)
            out_file = os.path.join(out_dir, fname)
            with open(out_file, 'wb') as f:
                f.write(z.read(name))
            try:
                im = Image.open(out_file)
                print(f'{fname}: size={im.size}, mode={im.mode}, format={im.format}')
            except Exception as e:
                print(f'{fname}: Error opening: {e}')
