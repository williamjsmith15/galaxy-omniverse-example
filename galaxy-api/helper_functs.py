import uuid
import os
import json
import tempfile
import logging as log

from os import remove
from os import path

from bioblend.galaxy import GalaxyInstance


def new_upload(gi, history, name, string):
    """
    Function to upload a string to a galaxy history as a dataset
        write the string to a file then upload the file to the history
        then remove the file

    Args:
        gi (GalaxyInstance): GalaxyInstance object
        history (string): History ID
        name (string): Name of the dataset
        string (string): String to be uploaded to the history

    Returns:
        upload (dict): Dictionary of the uploaded dataset
    """
    with open(name, 'w') as f:
        f.write(string)
    upload = gi.tools.upload_file(name, history)
    remove(name)
    return upload


def check_server_api(server, api_key):
    """
    Function to check if the provided API key and server address are valid

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key

    Returns:
        True if server and api key are valid
        False if server or api key are invalid
    """
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


def check_workflow(server, api_key, workflow_name):
    """
    Function to check if the workflow that is being referenced is part of
    the workflows available on the galaxy instance

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key
        workflow_name (string): Target workflow name

    Returns:
        True if workflow exists
        False if workflow does not exist
    """
    workflow_galaxy = get_workflows(server, api_key)

    if workflow_name not in workflow_galaxy:
        log.error(f"Workflow {workflow_name} not found on galaxy instance")
        return False
    else:
        return True


def launch_workflow(
    server,
    api_key,
    workflow_name,
    inputs,
    uid=None,
    from_omni=False
):
    """
    Function to call galaxy workflow via API

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key
        workflow_name (string): Target workflow name
        inputs (dict): Dictionary of inputs for the workflow, these should
            be named the same as the inputs in the workflow
            format: {input_name: input_string/filename, ...}
        uid (string): Unique identifier for the workflow run
        from_omni (bool): If true, the function will save the files to a
            location where they can be accessed by the omniverse extension

    Returns:
        True if workflow successfully launched
        False if workflow failed to launch
    """
    # Check server and api key are valid
    if not check_server_api(server=server, api_key=api_key):
        return False
    # Check workflow is accessible / exists
    if not check_workflow(
        server=server,
        api_key=api_key,
        workflow_name=workflow_name
    ):
        return False

    expected_inputs = get_inputs(
                                server=server,
                                api_key=api_key,
                                workflow_name=workflow_name
                            )

    gi = GalaxyInstance(url=server, key=api_key)

    # Create new history with name history_name
    if uid is None:
        uid = str(uuid.uuid4())

    new_hist = gi.histories.create_history(name=workflow_name + '_' + uid)

    # Upload files and parameters to the history
    workflow_inputs = {}

    # Setup wf_inputs for the workflow
    for wf_input in expected_inputs:

        if wf_input[0] == "dataset":
            uploads = []
            for name, string in inputs.items():
                if wf_input[1] != name:
                    continue
                # Check for case of input being a file or a string
                if path.isfile(string):
                    # Input is a file
                    uploads.append(
                        gi.tools.upload_file(string, new_hist['id'])
                    )
                else:
                    # Input is a string
                    uploads.append(
                        new_upload(gi, new_hist['id'], name, string)
                    )
            workflow_inputs[str(wf_input[2])] = {
                'src': 'hda',
                'id': uploads[-1]['outputs'][0]['id']
            }
        elif wf_input[0] == "parameter":
            for name, string in inputs.items():
                if wf_input[1] == name:
                    workflow_inputs[str(wf_input[2])] = string

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

    # Find the job created by the invocation
    job = gi.jobs.get_jobs(invocation_id=invocation_id)
    # Wait for this job to finish
    gi.jobs.wait_for_job(job_id=job[0]['id'])

    # From omniverse we want to save files in a location where we can access
    # Pull all the files from the history and save them to a temp location
    if from_omni:
        tempdir = tempfile.TemporaryDirectory()
        for dataset in gi.datasets.get_datasets(history_id=new_hist['id']):
            download = gi.datasets.download_dataset(
                file_path=tempdir.name,
                dataset_id=dataset['id'],
                use_default_filename=True
            )
        download = gi.invocations.get_invocation_biocompute_object(
            invocation_id=invocation_workflow[0]['id']
        )
        dict_to_save = json.dumps(download)
        bco_fname = tempdir.name + os.sep + 'biocompute_object.json'
        with open(bco_fname, 'w') as f_write:
            f_write.write(dict_to_save)

        gi.histories.delete_history(history_id=new_hist['id'])
        return tempdir


def get_inputs(server, api_key, workflow_name):
    """
    Function to get an array of inputs for a given galaxy workflow

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key
        workflow_name (string): Target workflow name

    Returns:
        inputs (array of strings): Input files expected by the workflow, these
            will be in the same order as they should be given in the main call
            format: [(type, name, id), ...]
    """
    # Check server and api key are valid
    if not check_server_api(server=server, api_key=api_key):
        return False
    # Check workflow exists
    if not check_workflow(
        server=server,
        api_key=api_key,
        workflow_name=workflow_name
    ):
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
            for wf_input in inputs:
                input_array.append(
                    ('dataset', wf_input['name'])
                )
        if len(inputs) > 0 and name == "Input parameter":
            for wf_input in inputs:
                input_array.append(
                    ('parameter', wf_input['name'])
                )

    return input_array


def get_outputs(server, api_key, workflow_name):
    """
    Function to get an array of outputs for a given galaxy workflow

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key
        workflow_name (string): Target workflow name

    Returns:
        outputs (array of strings): Output files given by the workflow,
            these are the names that can be requested as workflow outputs
    """
    # Check server and api key are valid
    if not check_server_api(server=server, api_key=api_key):
        return False
    if not check_workflow(
        server=server,
        api_key=api_key,
        workflow_name=workflow_name
    ):
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


def get_workflows(server, api_key):
    """
    Function to get an array of workflows available on a given galaxy instance

    Args:
        server (string): Galaxy server address
        api_key (string): User generated string from galaxy instance
            to create: User > Preferences > Manage API Key > Create a new key

    Returns:
        workflows (array of strings): Workflows available to be run on the
            galaxy instance provided
    """
    # Check server and api key are valid
    if not check_server_api(server=server, api_key=api_key):
        return False

    gi = GalaxyInstance(url=server, key=api_key)
    workflows_dict = gi.workflows.get_workflows()
    workflows = []
    for item in workflows_dict:
        workflows.append(item['name'])
    return workflows
