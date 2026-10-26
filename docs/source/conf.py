# pylint: disable=invalid-name,redefined-builtin,wrong-import-position
"""
Sphinx configuration of the smarter-types documentation, published to https://docs.smarter-types.smarter.sh/.

Build it with ``make sphinx-build``, which treats every warning as an error,
and publish it with ``make sphinx-publish``.
"""

import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
# autodoc imports the package from the source tree, installed or not.
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from smarter_types import __version__  # noqa: E402

# -- Project ------------------------------------------------------------------

project = "smarter-types"
author = "Lawrence McDaniel"
copyright = f"{date.today().year}, {author}"  # noqa: A001
version = __version__
release = __version__

SITE_URL = "https://docs.smarter-types.smarter.sh/"
GITHUB_URL = "https://github.com/smarter-sh/smarter-types"

# -- General ------------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "notfound.extension",
    "sphinx_sitemap",
]

# _templates/footer.html adds The Smarter Project to every page's footer.
templates_path = ["_templates"]
exclude_patterns: list[str] = []
language = "en"

# docstrings carry their own :type: and :rtype: fields, so signatures keep the annotations.
autodoc_typehints = "signature"
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "show-inheritance": True}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# copy only the code, not the prompts of console examples.
copybutton_prompt_text = r"\$ |>>> |\.\.\. "
copybutton_prompt_is_regexp = True

# -- HTML -----------------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = f"smarter-types {__version__}"
html_short_title = "smarter-types"
html_baseurl = SITE_URL
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
    "style_external_links": True,
    "prev_next_buttons_location": "both",
}
# the "Edit on GitHub" link at the top of each page.
html_context = {
    "display_github": True,
    "github_user": "smarter-sh",
    "github_repo": "smarter-types",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}
html_show_sourcelink = False
html_copy_source = False
html_extra_path = ["_extra"]

# sitemap.xml lists every page under the site's root, without a version prefix.
sitemap_url_scheme = "{link}"

# 404.html is served by CloudFront for every missing page, at any depth, so its links are absolute.
notfound_urls_prefix = "/"
