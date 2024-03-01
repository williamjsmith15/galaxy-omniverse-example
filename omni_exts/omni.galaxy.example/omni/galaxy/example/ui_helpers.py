import os
import json
from datetime import datetime

import omni.ui as ui
import omni.usd


class MinimalItem(ui.AbstractItem):
    def __init__(self, text):
        super().__init__()
        self.model = ui.SimpleStringModel(text)


class MinimalModel(ui.AbstractItemModel):
    def __init__(self, items, value=0):
        # Items is a 1D array of strings that are the options for the dropdown
        super().__init__()

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(
            lambda a: self._item_changed(None))

        self._items = [
            MinimalItem(text)
            for text in items
        ]

        self._current_index.set_value(value)

    def get_item_children(self, item):
        return self._items

    def get_item_value_model(self, item, column_id):
        if item is None:
            return self._current_index
        return item.model

    def set_model_state(self, value=0):
        self._current_index.set_value(value)


def import_USD(path_to_import):
    stage = omni.usd.get_context().get_stage()

    basename = os.path.splitext(os.path.basename(path_to_import))[0]
    cleaned_basename = [c for c in basename if c.isalnum() or c.isspace()]
    basename = "".join(cleaned_basename)
    prim = stage.DefinePrim(f"/{basename}", 'Xform')
    prim.GetReferences().AddReference(f'file:{path_to_import}')


def add_uid_to_prov(uid, wf_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    parent_path = current_path.split('omni_exts')[0]
    data_path = os.path.join(parent_path, "omni-data")

    uid_previous = {}

    file_path = os.path.join(data_path, "uid_track.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            uid_previous = json.load(file)

    uid_previous[uid] = f'{wf_name} at {datetime.now()}'

    with open(file_path, 'w') as file:
        json.dump(uid_previous, file)
