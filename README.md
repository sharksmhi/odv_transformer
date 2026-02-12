# ODV Transformer

Python 3 library developed by SHD at SMHI.

- Convert data into ICES ODV delivery format.
- Convert data into SeaDataNet ODV delivery format.

---

## How to run the main scripts

The scripts are located in `src/odv_transformer/run_code/`.  
Use `uv run -m` to execute them within the project virtual environment.

Run any of the following after updating paths:

uv run -m odv_transformer.run_code.ices_odv_writer_profile_archive
uv run -m odv_transformer.run_code.ices_odv_writer_phyche_archive
uv run -m odv_transformer.run_code.ices_odv_writer_merge_archives

---

## Contributing

Please follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guidelines and  
limit lines of code to 80 characters whenever possible and when it doesn't hurt readability.  
ODV-Transformer follows [Google Style Docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)  
for all code API documentation. When in doubt, use the existing code as a guide for coding style.
