# omniverse-workflows-fusion

Setup:

0. If on Windows install WSL2 and Ubuntu 20.04 LTS

1. Install Docker (or Docker Desktop on Windows)

2. Run the start script:

    `./start-galaxy.sh`

To modify or add tools:

1. Create / modify tools

2. Add tool to the tool_conf.xml file in the galaxy-config folder (see the example in the xml file for the openmc tool)

3. Restart the galaxy container:

    `./restart-galaxy.sh`
