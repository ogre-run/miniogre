.PHONY: clean setup_venv virtualenv build clean_build uninstall install clean_install print_version help

# python = ">=3.10,<4.0"
PYTHON=python3.10

clean:
	@echo "Cleaning up project..."
	@rm -rf env
	@echo "Project clean complete."

setup_venv:
	@echo "Setting up virtual environment..."
	@$(PYTHON) -m venv env
	@. env/bin/activate && $(PYTHON) -m pip install --upgrade pip setuptools
	@. env/bin/activate && $(PYTHON) -m pip install -r requirements.txt
	@. env/bin/activate && $(PYTHON) -m pip -V
	@echo "Virtual environment is ready."

virtualenv:
	@if [ -d "env" ]; then \
		echo "Virtual environment already exists."; \
		read -p "Do you want to delete it and create a new one? [y/N] " answer; \
		case $$answer in \
			[Yy]* ) \
				echo "Deleting and recreating the virtual environment..."; \
				rm -rf env; \
				$(MAKE) setup_venv;; \
			* ) \
				echo "Using the existing virtual environment.";; \
		esac \
	else \
		$(MAKE) setup_venv; \
	fi

build:
	@echo "Building package..."
	@rm -rf dist
	@. env/bin/activate && poetry build
	@echo "Package built."

clean_build: clean virtualenv build

uninstall:
	@echo "Uninstalling package..."
	@. env/bin/activate && $(PYTHON) -m pip uninstall -y miniogre
	@echo "Package uninstalled."

install: uninstall
	@echo "Installing from dist..."
	@. env/bin/activate && $(PYTHON) -m pip install dist/miniogre*.whl
	@echo "Installed."

clean_install: clean_build install

print_version:
	@. env/bin/activate && $(PYTHON) -m pip show miniogre
	@. env/bin/activate && $(PYTHON) -c "import miniogre; print(miniogre.__website__)"

help:
	@cat Makefile
