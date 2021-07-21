from __main__ import app
from flask import Flask, render_template, redirect, url_for, flash, g, request, abort, Response

@app.errorhandler(403)
def forbidden(e):
    return render_template('path_error/403.html'), 403

app.register_error_handler(403, forbidden)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('path_error/404.html'), 404

app.register_error_handler(404, page_not_found)

@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('path_error/413.html'), 413

app.register_error_handler(413, forbidden)