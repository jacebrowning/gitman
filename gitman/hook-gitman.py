# pyinstaller hook

from PyInstaller.utils.hooks import copy_metadata


# Normally PyInstaller does not include metadata files.
# necessary to find the 'gitman' distribution
# via the get_distribution function
datas = copy_metadata('gitman')
