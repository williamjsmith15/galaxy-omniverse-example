from helper_functs import get_workflows, get_inputs, get_outputs, launch_workflow

server = 'localhost:8080'
api_key = ''
workflow_name = ''

inputs = {
    'input1': 'path/to/input1.txt',
    'input2': 'path/to/input2.txt'
}

print(get_workflows(server, api_key))

print(get_inputs(server, api_key, workflow_name))

print(get_outputs(server, api_key, workflow_name))

launch_workflow(server, api_key, workflow_name, inputs)
