# Overview

This module contains Rust code, built by a package called Maturin.
Essentially:

1. Write Rust code (in ```src``` dir)
2. Build using Maturin (```(cd services/backend/app/src/modules/rcalc && maturin build --release --manylinux off --strip)```)

It builds a python wheel in ```target/wheels``` which is then installed as any other Python package in the backend Dockerfile

3. Run docker compose stack as usual

Can also use the ```up.sh``` file in project root which will build the rust lib as well before launching

# Create from scratch

Ensure Maturin Python lib is installed:
* Include in ```services/backend/app/requirements/dev.txt```
* ```pip install -r services/backend/app/requirements/dev.txt```

* Create new root folder for module and cd into it, e.g. ```services/backend/app/modules/tax```
* Create new Rust project using Maturin inside module folder, e.g. ```maturin new rst_tax_calculator```
* Write Rust code in ```tax/rst_tax_calculator/src/lib.rs```
* Compile with ```maturin build --release --manylinux off --strip``` from ```rst_tax_calculator/``` folder
* Wheel produced in ```rst_tax_calculator/target/wheels```
* Add to ```Dockerfile``` for copying
* Add relevant artifacts to ```.dockerignore``` and ```.gitignore```

# Notes

## Clean up untracked leftover files when switching away from this branch
```git clean -f -d -X .```
