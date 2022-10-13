import os

_separator = '='
component_dir = os.path.join(__file__.replace(os.path.basename(__file__), '')
                             .replace(os.path.sep + 'builder', ''), 'components')
element_name = 'JarvisBackend'
