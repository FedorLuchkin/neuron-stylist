import path_editor
import os
import zipfile
if not os.path.exists('beckend/vgg_conv.pth'):
    
    with zipfile.ZipFile('backend/vgg_conv.zip', 'r') as zip_ref:
        zip_ref.extractall('backend')