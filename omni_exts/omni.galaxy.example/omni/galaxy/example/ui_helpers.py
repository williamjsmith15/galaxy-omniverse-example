import os

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

