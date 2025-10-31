"""
Pulsar Workflow Engine Documentation
====================================

Pulsar is a declarative workflow engine for orchestrating AI agents in YAML-defined workflows.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'Pulsar'
copyright = f'{datetime.now().year}, Pulsar Team'
author = 'Pulsar Team'
release = '0.1.1'
version = '0.1.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx_rtd_theme',
    'myst_parser',
]

# MyST Parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
    'special-members': '__init__',
}

autodoc_typehints = 'description'
autoclass_content = 'both'

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# -- Options for manual page output ------------------------------------------

man_pages = [
    ('index', 'pulsar', 'Pulsar Documentation', [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    ('index', 'Pulsar', 'Pulsar Documentation', author, 'Pulsar',
     'A declarative workflow engine for orchestrating AI agents', 'Miscellaneous'),
]

# -- Extension configuration --------------------------------------------------

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pydantic': ('https://docs.pydantic.dev/latest/', None),
    'click': ('https://click.palletsprojects.com/en/8.1.x/', None),
    'jinja2': ('https://jinja.palletsprojects.com/en/3.1.x/', None),
    'rich': ('https://rich.readthedocs.io/en/stable/', None),
}

# Todo extension
todo_include_todos = True

# Coverage extension
coverage_modules = [
    'agents',
    'engine',
    'models',
    'cli',
]

# -- Custom functions ---------------------------------------------------------

def setup(app):
    """Setup function for Sphinx extensions."""
    app.add_css_file('custom.css')