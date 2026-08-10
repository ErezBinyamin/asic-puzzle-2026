#!/bin/bash
bootstrap() {
	# Standard packages
	PACKAGES=()

	# Good gui software
	PACKAGES+=("klayout")

	# Do the installation
	for pkg in ${PACKAGES[@]}
	do
		dpkg -s $pkg &>/dev/null || sudo apt install --yes ${pkg} && echo [COMPLETE] ${pkg}
	done
}

# Main
export PS4='\033[0;33m$0:$LINENO [$?]+ \033[0m '
bootstrap
set -x
klayout -b -r extract_cell_pins.py 04_final.gds
