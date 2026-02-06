from flask import Blueprint, render_template, request, redirect, url_for, session
import hashlib
import sqlite3

bp = Blueprint('dashboard', __name__)

# @bp.route("/")
# def index():
#     return redirect("student/courses")