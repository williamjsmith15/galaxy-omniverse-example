__all__ = ["Window"]

# Add the api helper functions to the python path
import sys
import os
import json
import asyncio
import uuid
import shutil
from pprint import pprint
import carb
import omni.ui as ui

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = current_path.split('omni_exts')[0]
api_path = os.path.join(parent_path, "galaxy-api")
data_path = os.path.join(parent_path, "omni-data")
sys.path.append(api_path)

from helper_functs import launch_workflow, get_workflows, get_inputs, get_outputs
from .ui_helpers import MinimalModel

LABEL_WIDTH = 50
HEIGHT = 300
SPACING = 4

path = os.path.join(current_path, "default.json")

if os.path.exists(path):
    carb.log_info(f"Loading default settings from {path}")
    with open(path) as f_read:
        default = json.load(f_read)
else:
    carb.log_info(f"Could not find {path}, using hardcoded defaults")
    default = {
        "galaxy_server": "localhost:8080",
        "galaxy_api_key": "",
        "workflow_idx": 0,
        "workflow_inputs": {},
        "selected_folder_idx": 0,
        "selected_file_idx": 0,
    }


collapsible_frames_default = {
    "Server Settings": True,
    "Workflow Message Composer": False,
}


def fire_and_forget(f):
    '''To wrap a function for a fire and forget call.'''
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)
    return wrapped


class Window(ui.Window):
    """The class that represents the window"""

    # Setting up dicts that hold the UI elements
    settings = {}
    frames = {}

    # Initialise the lists that hold the workflows and inputs
    workflows = []
    workflow_inputs = []
    workflow_outputs = []

    # Initialise the lists that hold the folders and files
    folders = []
    files = []

    initial_build = True

    output_field = None
    output_prev_commands = ""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        # Set the function that is called to build widgets when the window is
        # visible
        self.frame.set_build_fn(self._build_fn)

    def destroy(self):
        '''It will destroy all the children'''
        super().destroy()

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()

    ##################################
    # --- BUILD FRAMES & FUNCTIONS ---
    ##################################

    def _build_API(self):
        if not self.initial_build:
            self._write_settings()

        # Build the widgets of the Run group
        with self._build_frame("Server Settings"):
            with ui.VStack(height=0, spacing=SPACING):
                self._build_server_settings()

        with self._build_frame("Workflow Message Composer"):
            with ui.VStack(height=0, spacing=SPACING):
                self._build_workflow_message_composer()

        ui.Label("Info", width=self.label_width)
        output_field_string_model = ui.SimpleStringModel("")
        self.output_field = ui.StringField(
            output_field_string_model,
            height=HEIGHT,
            multiline=True).model
        self.output_field.set_value(self.output_prev_commands)

        self.initial_build = False

    def _write_settings(self):
        for key, value in self.settings.items():
            val_type = type(value)
            if val_type is ui._ui.SimpleStringModel:
                default[key] = value.get_value_as_string()
            elif val_type is ui._ui.SimpleIntModel:
                default[key] = value.get_value_as_int()
            elif val_type is ui._ui.SimpleFloatModel:
                default[key] = value.get_value_as_float()
            elif val_type is dict:
                for sub_key, sub_value in value.items():
                    try:
                        default[key][sub_key] = sub_value.get_value_as_string()
                    except AttributeError:
                        carb.log_error(
                            f"""Error with key {key}, subkey {sub_key}.
                            No dict written yet for this: {AttributeError}"""
                        )
            else:
                try:
                    temp = value.get_item_value_model(None, 1)
                    default[key] = temp.get_value_as_int()
                except AttributeError:
                    carb.log_error(f"Error with key {key}: {AttributeError}")
                except Exception:
                    carb.log_error(f"Error: {Exception}")
                    carb.log_error(f"Don't know how to handle {key}")

    def _build_server_settings(self):
        ui.Label("Galaxy Server Settings", width=self.label_width)
        with ui.HStack(height=0, spacing=SPACING):
            ui.Label("Galaxy Server Address:")
            self.settings["galaxy_server"] = ui.StringField().model
            self.settings["galaxy_server"].set_value(default["galaxy_server"])

        with ui.HStack(height=0, spacing=SPACING):
            ui.Label("API Key:")
            self.settings["galaxy_api_key"] = ui.StringField(password_mode=True).model
            self.settings["galaxy_api_key"].set_value(default["galaxy_api_key"])

    def _build_workflow_message_composer(self):
        ui.Button("Get Workflows", clicked_fn=lambda: self._get_workflows())

        if len(self.workflows) > 0:
            ui.Label("Workflows:")
            self.settings["workflow_idx"] = MinimalModel(self.workflows)
            self.settings["workflow_idx"].set_model_state(default["workflow_idx"])
            ui.ComboBox(self.settings["workflow_idx"])

            # Only want get_inputs when we have the workflows
            ui.Button("Get Inputs", clicked_fn=lambda: self._get_inputs())

        if len(self.workflow_inputs) > 0 and len(self.workflows) > 0:
            ui.Label("Inputs:")
            self.settings["workflow_inputs"] = {}
            for input_type, name in self.workflow_inputs:
                with ui.HStack(height=0, spacing=SPACING):
                    ui.Label(name)
                    ui.Label(input_type)
                    if input_type == "dataset":
                        # File selector, alllow local files to be selected
                        ui.Label("Yet to be implemented")
                    else:
                        if name == "password":
                            self.settings["workflow_inputs"][name] = ui.StringField(password_mode=True).model
                        else:
                            self.settings["workflow_inputs"][name] = ui.StringField().model
                        if name in default["workflow_inputs"].keys():
                            self.settings["workflow_inputs"][name].set_value(default["workflow_inputs"][name])
            # Only want launch_workflow when we have the inputs
            ui.Button("Launch Workflow", clicked_fn=lambda: self._launch_workflow())

    def _build_frame(self, frame_name):
        """To Build a Collapsable Frame"""
        collapsed = collapsible_frames_default[frame_name]
        self.frames[frame_name] = ui.CollapsableFrame(frame_name, collapsed=collapsed)
        return self.frames[frame_name]

    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        with ui.ScrollingFrame():
            with ui.VStack(height=0):
                self._build_API()

    ##########################
    # --- BUTTONS ---
    ##########################

    def _refresh_screen(self):
        """
        Writes the current state of the collpsable frames to the global dict
        Then refreshes the UI
        """
        global collapsible_frames_default

        for frame, model in self.frames.items():
            collapsible_frames_default[frame] = model.collapsed

        self.frame.rebuild()

    def _get_workflows(self):
        server = self.settings["galaxy_server"].get_value_as_string()
        api_key = self.settings["galaxy_api_key"].get_value_as_string()

        self.workflows = get_workflows(server, api_key)
        self._new_print(f"Workflows: {self.workflows}")
        self._refresh_screen()

    def _get_inputs(self):
        server = self.settings["galaxy_server"].get_value_as_string()
        api_key = self.settings["galaxy_api_key"].get_value_as_string()

        workflow_idx = self.settings["workflow_idx"].get_item_value_model(None, 1).get_value_as_int()
        workflow = self.workflows[workflow_idx]

        for input_type, name, idx in get_inputs(server, api_key, workflow):
            self.workflow_inputs.append((input_type, name))
        self._new_print(f"Inputs: {self.workflow_inputs}")
        self._refresh_screen()

    def _get_outputs(self):
        server = self.settings["galaxy_server"].get_value_as_string()
        api_key = self.settings["galaxy_api_key"].get_value_as_string()

        workflow_idx = self.settings["workflow_idx"].get_item_value_model(None, 1).get_value_as_int()
        workflow = self.workflows[workflow_idx]

        self.workflow_outputs = get_outputs(server, api_key, workflow)
        self._new_print(f"Outputs: {self.workflow_outputs}")
        self._refresh_screen()

    def _launch_workflow(self):
        server = self.settings["galaxy_server"].get_value_as_string()
        api_key = self.settings["galaxy_api_key"].get_value_as_string()

        inputs = {}

        workflow_idx = self.settings["workflow_idx"].get_item_value_model(None, 1).get_value_as_int()
        workflow = self.workflows[workflow_idx]

        for workflow_input in self.workflow_inputs:
            input_name = workflow_input[1]
            value = self.settings["workflow_inputs"][input_name].get_value_as_string()
            inputs[input_name] = value

        self._new_print(f"Launching workflow {workflow} with inputs {inputs}")
        self._async_launch(server, api_key, workflow, inputs)
        self._new_print("Workflow launched")

    def _new_print(self, console_text):
        self.output_prev_commands += f"{console_text}\n"
        self.output_field.set_value(self.output_prev_commands)
        carb.log_info(console_text)

    def _get_folders(self):
        for uid in os.listdir(data_path):
            self.folders.append(uid)

    def _get_files(self, uid):
        for file in os.listdir(data_path + os.sep + uid):
            self.files.append(file)

    def _pull_file(self, uid, file):
        carb.log_info(f"Pulling {file} from {uid}")
        file_path = data_path + os.sep + uid + os.sep + file
        if not os.path.exists(file_path):
            carb.log_error(f"File {file} does not exist in {uid}")
            return
        ext = os.path.splitext(file_path)[-1]
        if ext == ".json":
            with open(file_path) as f_read:
                data = json.load(f_read)
                pprint(data)
                self._new_print(f"File {file} from {uid}:\n{data}")
        elif ext == ".txt":
            with open(file_path) as f_read:
                data = f_read.read()
                self._new_print(f"File {file} from {uid}:\n{data}")
        elif 'usd' in ext:
            carb.log_info(f"Opening {file_path}")
            carb.log_error("USD File IO not yet implemented")
        else:
            carb.log_error(f"File type {ext} not yet implemented")
            

    @fire_and_forget
    def _async_launch(self, server, api_key, workflow, inputs):
        uid = str(uuid.uuid4())
        tempdir = launch_workflow(server, api_key, workflow, inputs, uid, True)

        if not os.path.exists(data_path):
            os.mkdir(data_path)

        os.mkdir(data_path + os.sep + uid)

        for file_name in os.listdir(tempdir.name):
            file = tempdir.name + os.sep + file_name
            carb.log_info(f"File: {file}")
            shutil.move(file, data_path + os.sep + uid + os.sep + file_name)

        tempdir.cleanup()
