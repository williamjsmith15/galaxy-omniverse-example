from helper_functs import get_workflows, get_inputs, get_outputs, launch_workflow

server = 'localhost:8080'
api_key = ''
workflow_name = ''

inputs = {
    'CAD': '../test_files/dagmc.h5m',
    'JSON_Config': '../test_files/openmc_config.json',
}

print(get_workflows(server, api_key))

print(get_inputs(server, api_key, workflow_name))

print(get_outputs(server, api_key, workflow_name))

launch_workflow(server, api_key, workflow_name, inputs)
