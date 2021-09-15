import werkzeug
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import flask, os

from __main__ import app

def upload_img(file: werkzeug.datastructures.FileStorage, path: str, *args: list[str]) -> bool:
    """Method to upload an image in a specific folder. Args can be used to change the name of the uploaded file. 
    For example, uuid_old_name.jpg

    Args:
        file (werkzeug.datastructures.FileStorage): File object from a wtf file input.
        path (str): Path were to upload the image.

    Returns:
        bool: Return True if successful, False otherwise.
    """
    filename = secure_filename(file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[-1]
        filename = (args[0] + filename) if args else filename
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flask.abort(403)
        file.save(os.path.join(path, filename))
        return True
    return False
