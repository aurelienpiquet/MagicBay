from flask import Flask, render_template, redirect, url_for, flash, g, request, abort, Response, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, ForeignKey, text, column, desc, or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, current_user, logout_user
#from flask_ckeditor import CKEditor, CKEditorField
from wtforms import *
from wtforms.validators import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
import werkzeug.exceptions
from turbo_flask import Turbo


from PIL import Image
import sys, os, logging, datetime, sqlalchemy.exc, io, base64, pprint, time


