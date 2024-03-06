:: Upgrade pip & wheel
python -m pip install --upgrade pip wheel

::Install prebuild wheel
python -m pip install --extra-index-url https://pypi.vnpy.com TA_Lib==0.4.24

:: Install vnpy_crypto
python -m pip install .