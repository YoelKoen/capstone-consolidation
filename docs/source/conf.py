import os
import sys
import django

# 1. Point Sphinx to the folder where manage.py is
sys.path.insert(0, os.path.abspath("../../"))

# 2. Use 'news_system' because that is the folder containing your settings.py
os.environ["DJANGO_SETTINGS_MODULE"] = "news_system.settings"

# 3. Initialize Django
django.setup()

# -- Project information -----------------------------------------------------
project = "My Capstone"
copyright = "2026, Yoel"
author = "Yoel"
release = "1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = "alabaster"
html_static_path = ["_static"]
