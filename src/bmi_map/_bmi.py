from bmi_map._parameter import Parameter

BMI = {
    "finalize": (),
    "get_bmi_version": (Parameter(name="version", intent="out", type="string"),),
    "get_component_name": (Parameter(name="name", intent="out", type="string"),),
    "get_current_time": (Parameter(name="time", intent="out", type="double"),),
    "get_end_time": (Parameter(name="time", intent="out", type="double"),),
    "get_grid_edge_count": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="count", intent="out", type="int"),
    ),
    "get_grid_edge_nodes": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="edge_nodes", intent="in", type="array[int]"),
    ),
    "get_grid_face_count": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="count", intent="out", type="int"),
    ),
    "get_grid_face_edges": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="face_edges", intent="in", type="array[int]"),
    ),
    "get_grid_face_nodes": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="face_nodes", intent="in", type="array[int]"),
    ),
    "get_grid_node_count": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="count", intent="out", type="int"),
    ),
    "get_grid_nodes_per_face": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="nodes_per_face", intent="in", type="array[int]"),
    ),
    "get_grid_origin": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="origin", intent="in", type="array[double]"),
    ),
    "get_grid_rank": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="rank", intent="out", type="int"),
    ),
    "get_grid_shape": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="shape", intent="in", type="array[int]"),
    ),
    "get_grid_size": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="size", intent="out", type="int"),
    ),
    "get_grid_spacing": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="spacing", intent="in", type="array[double]"),
    ),
    "get_grid_type": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="type", intent="out", type="string"),
    ),
    "get_grid_x": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="x", intent="in", type="array[double]"),
    ),
    "get_grid_y": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="y", intent="in", type="array[double]"),
    ),
    "get_grid_z": (
        Parameter(name="grid", intent="in", type="int"),
        Parameter(name="z", intent="in", type="array[double]"),
    ),
    "get_input_item_count": (Parameter(name="count", intent="out", type="int"),),
    "get_input_var_names": (
        Parameter(name="names", intent="out", type="array[string]"),
    ),
    "get_output_item_count": (Parameter(name="count", intent="out", type="int"),),
    "get_output_var_names": (
        Parameter(name="names", intent="out", type="array[string]"),
    ),
    "get_start_time": (Parameter(name="time", intent="out", type="double"),),
    "get_time_step": (Parameter(name="time_step", intent="out", type="double"),),
    "get_time_units": (Parameter(name="units", intent="out", type="string"),),
    "get_value": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="dest", intent="in", type="array[any]"),
    ),
    "get_value_at_indices": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="dest", intent="in", type="array[int]"),
        Parameter(name="inds", intent="in", type="array[int, count]"),
    ),
    "get_value_ptr": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="dest_ptr", intent="out", type="array[any]"),
    ),
    "get_var_grid": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="grid", intent="out", type="int"),
    ),
    "get_var_itemsize": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="size", intent="out", type="int"),
    ),
    "get_var_location": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="location", intent="out", type="string"),
    ),
    "get_var_nbytes": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="nbytes", intent="out", type="int"),
    ),
    "get_var_type": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="type", intent="out", type="string"),
    ),
    "get_var_units": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="units", intent="out", type="string"),
    ),
    "initialize": (Parameter(name="config_file", intent="in", type="string"),),
    "set_value": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="src", intent="in", type="array[any]"),
    ),
    "set_value_at_indices": (
        Parameter(name="name", intent="in", type="string"),
        Parameter(name="inds", intent="in", type="array[int, count]"),
        Parameter(name="src", intent="in", type="array[any]"),
    ),
    "update": (),
    "update_until": (Parameter(name="time", intent="in", type="double"),),
}
