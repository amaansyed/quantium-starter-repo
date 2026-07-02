import app as app_module


def find_component_by_id(component, target_id):
    if getattr(component, "id", None) == target_id:
        return component

    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            found = find_component_by_id(child, target_id)
            if found is not None:
                return found
    elif children is not None:
        return find_component_by_id(children, target_id)

    return None


def test_header_is_present():
    header = find_component_by_id(app_module.app.layout, "header-title")
    assert header is not None
    assert header.children == "Soul Foods Pink Morsel Sales Visualiser"


def test_visualisation_is_present():
    graph = find_component_by_id(app_module.app.layout, "sales-graph")
    assert graph is not None


def test_region_picker_is_present():
    picker = find_component_by_id(app_module.app.layout, "region-radio")
    assert picker is not None
    assert picker.value == "all"
