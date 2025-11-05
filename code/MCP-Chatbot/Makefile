SHELL := /bin/bash

set-google-creds:
	@echo "Setting GOOGLE_APPLICATION_CREDENTIALS..."
	@echo 'export GOOGLE_APPLICATION_CREDENTIALS="$(HOME)/.credentials/gcp-sa.json"' >> ~/.bashrc
	@echo "Added to ~/.bashrc. Run 'source ~/.bashrc' or open a new terminal to activate."

# After running the Makefile, reload
# source ~/.bashrc
# Now test $ echo $GOOGLE_APPLICATION_CREDENTIALS
# You should see: /home/your-username/.credentials/gcp-sa.json