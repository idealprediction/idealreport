"""
    idealreport wrapper for loading settings from a hjson file validating fields
"""
import os
import hjson
import idealreport

def load_settings():
    """ load settings from idealreport/settings.hjson, validate required fields
    """
    # idealreport directory and the settings.hjson file
    idealreport_path = os.path.dirname(idealreport.settings.__file__)
    filename = os.path.join(idealreport_path, 'settings.hjson')

    # error if the settings.hjson file doesn't exist
    if not os.path.exists(filename):
        raise Exception('idealreport.settings ERROR: The settings.hjson file does not exist here: %s' % filename)

    # load the settings file
    settings = hjson.loads(open(filename).read())

    # error if key variables are missing
    for key in ['output_path']:
        if key not in settings:
            raise Exception('idealreport.settings ERROR: The settings.hjson file does not contain the required key: %s' % key)

    return settings
