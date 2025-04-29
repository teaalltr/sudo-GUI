"""
Composite widgets used by the sudo-GUI.

Only two public symbols are re-exported:

* SecurePathDialog
* SecurePathWidget
"""
from .secure_path import SecurePathDialog, SecurePathWidget

__all__: list[str] = ["SecurePathDialog", "SecurePathWidget"]
