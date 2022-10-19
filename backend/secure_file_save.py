import numpy as np
import path_editor
from backend import secure_file_open as of


def save_file(path, user_id, value, delete=False):
    file_save_status = 0
    while file_save_status == 0:
        try:
            file_json = of.open_file(path)
            if delete:
                del file_json[user_id]
            else:
                file_json[user_id] = value
            np.save(path, file_json)
            file_save_status = 1
        except OSError:
            file_save_status = 0
    return 0
