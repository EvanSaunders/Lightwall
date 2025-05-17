# Makefile for Lightwall Project

# Define variables
VIRTUAL_ENV=lightwall_env
PYTHON=$(VIRTUAL_ENV)/bin/python3
SCRIPT=newMain.py

# Target to create the virtual environment if it doesn't exist
create_env:
	@if [ ! -d "$(VIRTUAL_ENV)" ]; then \
		python3 -m venv $(VIRTUAL_ENV); \
		$(VIRTUAL_ENV)/bin/pip install --upgrade pip; \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

# Target to activate the virtual environment and run the script
run: create_env
	@echo "Activating virtual environment and running the script..."
	@bash -c "source $(VIRTUAL_ENV)/bin/activate && sudo $(PYTHON) $(SCRIPT)"

kill:
	@echo "Killing all newMain.py instances..."
	@sudo pkill -9 -f newMain.py || true

