# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Path setup --------------------------------------------------------------

# Ajoute la racine du projet (SAE502-TaskFlow) au path pour autodoc
sys.path.insert(0, os.path.abspath('../../../'))

# -- Project information -----------------------------------------------------

project = 'SAE502-TaskFlow'
copyright = '2024, TaskFlow'
author = 'TaskFlow'
release = '1.0.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',          # Génère automatiquement la doc depuis les docstrings
    'sphinx.ext.napoleon',         # Support pour Google et NumPy docstrings
    'sphinx.ext.viewcode',         # Ajoute des liens vers le code source
    'sphinx.ext.todo',             # Support des TODO dans la documentation
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Autodoc configuration ---------------------------------------------------

autodoc_member_order = 'bysource'   # Trie les membres par ordre d'apparition dans le code
autodoc_typehints = 'description'  # Montre les types des annotations de fonctions
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# -- Napoleon settings (for Google/NumPy style docstrings) -------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# -- Todo extension settings -------------------------------------------------

todo_include_todos = True