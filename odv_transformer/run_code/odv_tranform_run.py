
import subprocess
import os

subprocess.run(f'set PYTHONPATH=%PYTHONPATH%;C:\LenaV\python3\sharksmhi\ctdpy')
subprocess.run(f'set PYTHONPATH=%PYTHONPATH%;C:\LenaV\python3\sharksmhi\odv_transformer')
subprocess.run(f"c:\Miniconda\Scripts\python w_odv_transformer\odv_transformer\main.py")
