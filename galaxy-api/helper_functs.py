from bioblend.galaxy import GalaxyInstance
from os import remove
import logging as log


def new_upload(gi, history, name, string):
    with open(name, 'w') as f:
        f.write(string)
    upload = gi.tools.upload_file(name, history)
    remove(name)
    return upload

def check_server_api(check_config):
    """
    Function to check if the provided API key and server address are valid
    """
    server = check_config['server']
    api_key = check_config['api_key']

    try:
        GalaxyInstance(url=server)
    except ValueError:
        log.error("Server address is not valid")
        return False

    try:
        gi = GalaxyInstance(url=server, key=api_key)
        gi.workflows.get_workflows()
    except Exception:
        log.error("API key is not valid")
        return False
    return True

def check_workflow(check_config):
    """
    Function to check if the workflow that is being referenced is part of
    the workflows available on the galaxy instance
    """

    workflow_galaxy = get_workflows(check_config)
    workflow_to_check = check_config['workflow_name']

    if workflow_to_check not in workflow_galaxy:
        log.error(f"Workflow {workflow_to_check} not found on galaxy instance")
        return False
    else:
        return True


def launch_workflow(launch_config):
    """
    Function to call galaxy workflow via API

    Usage:
        call_api(
            launch_config = json_launch
        )

    Args:
        launch_config (dict): dictionary containing server, api_key,
            workflow_name, and inputs
    """
    try:
        server = launch_config['server']
        api_key = launch_config['api_key']
        workflow_name = launch_config['workflow_name']
        inputs = launch_config['inputs']
        uid = launch_config['uid']
    except KeyError:
        log.error("Key error, one of the keys provided is not valid")
        return False

    # Check server and api key are valid
    if not check_server_api(launch_config):
        return False
    # Check workflow is accessible / exists
    if not check_workflow(launch_config):
        return False

    expected_inputs = get_inputs(launch_config)

    gi = GalaxyInstance(url=server, key=api_key)

    # Create new history with name history_name
    new_hist = gi.histories.create_history(name=uid)

    # Upload files and parameters to the history
    workflow_inputs = {}

    # Setup Inputs for the workflow
    for input in expected_inputs:

        if input[0] == "dataset":
            uploads = []
            for name, string in inputs.items():
                if input[1] == name:
                    uploads.append(
                        new_upload(gi, new_hist['id'], name, string)
                    )
            workflow_inputs[str(input[2])] = {
                'src': 'hda',
                'id': uploads[-1]['outputs'][0]['id']
            }
        elif input[0] == "parameter":
            for name, string in inputs.items():
                if input[1] == name:
                    workflow_inputs[str(input[2])] = string

    # Get list of workflows, searching for workflow with name workflow_name
    api_workflow = gi.workflows.get_workflows(name=workflow_name)

    # Check that all inputs are present before launching
    if len(workflow_inputs) != len(expected_inputs):
        log.error("Not all inputs were provided or were not named correctly")
        return False

    # Call workflow
    gi.workflows.invoke_workflow(
        workflow_id=api_workflow[0]['id'],
        inputs=workflow_inputs,
        history_id=new_hist['id']
    )

    # Gets the invocation of the above workflow and then waits for it to
    # complete (need to check max time on this - especially for long sim runs)
    invocation_workflow = gi.invocations.get_invocations(
        workflow_id=api_workflow[0]['id']
    )
    invocation_id = invocation_workflow[0]['id']
    gi.invocations.wait_for_invocation(invocation_id=invocation_id)

    return True


def get_inputs(get_inputs_config):
    """
    Function to get an array of inputs for a given galaxy workflow

    Usage:
        get_inputs(
            server = "http://mcfe.duckdns.org/",
            api_key = "ea8caa3beffee9c8d58c8b0a092d936e",
            workflow_name = "More Complex Test Workflow",
        )

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key
        workflow_name (string): Target workflow name
    Returns:
        inputs (array of strings): Input files expected by the workflow, these
        will be in the same order as they should be given in the main API call
    """
    try:
        server = get_inputs_config['server']
        api_key = get_inputs_config['api_key']
        workflow_name = get_inputs_config['workflow_name']
    except KeyError:
        log.error("Key error, one of the keys provided is not valid")
        return False

    # Check server and api key are valid
    if not check_server_api(get_inputs_config):
        return False
    # Check workflow exists
    if not check_workflow(get_inputs_config):
        return False

    gi = GalaxyInstance(url=server, key=api_key)
    api_workflow = gi.workflows.get_workflows(name=workflow_name)
    steps = gi.workflows.export_workflow_dict(api_workflow[0]['id'])['steps']
    input_array = []
    for step in steps:
        inputs = steps[step]['inputs']
        name = steps[step]['name']

        # Some of the steps don't take inputs so have to skip these
        # And only pull the inputs from input datasets, not individual tools
        if len(inputs) > 0 and name == "Input dataset":
            for input in inputs:
                input_array.append(
                    ('dataset', input['name'], steps[step]['id'])
                )
        if len(inputs) > 0 and name == "Input parameter":
            for input in inputs:
                input_array.append(
                    ('parameter', input['name'], steps[step]['id'])
                )

    return input_array


def get_outputs(get_outputs_config):
    """
    Function to get an array of outputs for a given galaxy workflow

    Usage:
        get_outputs(
            server = "http://mcfe.duckdns.org/",
            api_key = "ea8caa3beffee9c8d58c8b0a092d936e",
            workflow_name = "More Complex Test Workflow",
        )

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key
        workflow_name (string): Target workflow name
    Returns:
        outputs (array of strings): Output files given by the workflow,
            these are the names that can be requested as workflow outputs
    """
    try:
        server = get_outputs_config['server']
        api_key = get_outputs_config['api_key']
        workflow_name = get_outputs_config['workflow_name']
    except KeyError:
        log.error("Key error, one of the keys provided is not valid")
        return False

    # Check server and api key are valid
    if not check_server_api(get_outputs_config):
        return False
    if not check_workflow(get_outputs_config):
        return False

    gi = GalaxyInstance(url=server, key=api_key)
    api_workflow = gi.workflows.get_workflows(name=workflow_name)
    steps = gi.workflows.export_workflow_dict(api_workflow[0]['id'])['steps']
    outputs = []

    for step in steps:
        # Some of the steps don't take inputs so have to skip these
        if not len(steps[step]) > 0:
            continue

        if 'outputs' not in steps[step]:
            continue

        output_dict = steps[step]['outputs']

        if not len(output_dict) > 0:
            continue

        # See if output has been renamed & grab that name instead
        if 'post_job_actions' in steps[step]:
            post_job_actions = steps[step]['post_job_actions']
            if 'RenameDatasetActionFile' in post_job_actions:
                action_file = post_job_actions['RenameDatasetActionFile']
                name = action_file['action_arguments']['newname']
                outputs.append(name)
                continue

        for output in output_dict:
            outputs.append(output['name'])

    return outputs


def get_workflows(get_workflows_config):
    """
    Function to get an array of workflows available on a given galaxy instance

    Usage:
        get_workflows(
            config_dict
        )

    Args:
        get_workflows_config (dict): dictionary containing server and api_key
    Returns:
        workflows (array of strings): Workflows available to be run on the
            galaxy instance provided
    """
    # Check server and api key are valid
    if not check_server_api(get_workflows_config):
        return False

    try:
        server = get_workflows_config['server']
        api_key = get_workflows_config['api_key']
    except KeyError:
        log.error("Key error, one of the keys provided is not valid")
        return False

    gi = GalaxyInstance(url=server, key=api_key)
    workflows_dict = gi.workflows.get_workflows()
    workflows = []
    for item in workflows_dict:
        workflows.append(item['name'])
    return workflows