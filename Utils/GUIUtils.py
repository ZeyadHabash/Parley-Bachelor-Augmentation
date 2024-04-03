import ipywidgets

class GUIUtils:

    def get_button(desc, on_click):
        button = ipywidgets.widgets.Button(description=desc)
        button.on_click(on_click)
        return button

    def get_slider(desc, min, val, max):
        return ipywidgets.widgets.IntSlider(value=val, min=min, max=max, step=1,
                                            description=desc, disabled=False, continuous_update=False,
                                            orientation='horizontal', readout=True, readout_format='d')

    def get_text_box(desc, value="", default="Blank"):
        return ipywidgets.widgets.Text(value=value, placeholder=default, description=desc, disabled=False)

    def get_dropdown_list(desc, options, val=None):
        v = options[0] if val == None else val
        return ipywidgets.widgets.Dropdown(options=options, value=v, description=desc, disabled=False)

    def get_label(value):
        return ipywidgets.widgets.Label(value=value)

    def get_layout(pcs):
        return ipywidgets.Layout(width='100%', grid_template_rows='auto', grid_template_columns=pcs)

    def get_check_box(description, value):
        return ipywidgets.widgets.Checkbox(value=value, description=description, disabled=False, indent=False)
