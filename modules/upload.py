from werkzeug.utils import secure_filename
import flask, os

from __main__ import app

def upload_in_db(file, path, *args):
    filename = secure_filename(file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[-1]
        filename = args[0] + filename
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flask.abort(403)
        file.save(os.path.join(path, filename))
        return True
