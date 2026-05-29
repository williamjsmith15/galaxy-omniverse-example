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


Common issues:
 - On windows getting permissions errors, remove special characters:

   `sed -i -e 's/\r$//' start-galaxy.sh`
   
 - Then sort permissions:

   `chmod +x start-galaxy.sh`
   
 - And run as normal:

   `./start-galaxy.sh`

Caution:
 - The default.json file (from the default.json.template located at omni_exts/omni.galaxy.example/omni/galaxy/example/default.json.template) should contain an API key from the Galaxy instance for the extension to run correctly. If this is the case, treat this as a sensitive file and ensure it is not pushed to any public repository (it is already included in the .gitignore). The API key allows anyone with it to run jobs and access data on the associated account.
