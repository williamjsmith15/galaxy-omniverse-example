from helper_functs import get_workflows, get_inputs, get_outputs, launch_workflow

server = 'localhost:8080'

# For API key generation go to the galaxy instance
# Click user -> preferences -> manage API key
# Then either generate or copy the key and paste it below
api_key = ''

# For the workflow name, this is the name you have used in the creationg of the workflow
# This can be found either on the galaxy instance or running the get_workflows function
workflow_name = ''

# Again, these are the input names defined in the workflow, either use the names defined
# in the workflow or get the input names from running the get_inputs function
# The inputs are the paths to the input files or string to use as text based input
inputs = {
    'CAD': '../test_files/dagmc.h5m',
    'JSON_Config': '../test_files/openmc_config.json',
}

print(get_workflows(server, api_key))

print(get_inputs(server, api_key, workflow_name))

print(get_outputs(server, api_key, workflow_name))

launch = launch_workflow(server, api_key, workflow_name, inputs)

if launch:
    print('Workflow launched successfully')
else:
    print('Workflow failed to launch')
