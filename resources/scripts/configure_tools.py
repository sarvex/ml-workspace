#!/usr/bin/python

"""
Configure and run tools
"""


from subprocess import call
import os
import sys

# Enable logging
import logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', 
    level=logging.INFO, 
    stream=sys.stdout)

log = logging.getLogger(__name__)

ENV_RESOURCES_PATH = os.getenv("RESOURCES_PATH", "/resources")
ENV_WORKSPACE_HOME = os.getenv("WORKSPACE_HOME", "/workspace")
HOME = os.getenv("HOME", "/root")

DESKTOP_PATH = f"{HOME}/Desktop"

# Get jupyter token 
ENV_AUTHENTICATE_VIA_JUPYTER = os.getenv("AUTHENTICATE_VIA_JUPYTER", "false")

token_parameter = ""
if ENV_AUTHENTICATE_VIA_JUPYTER.lower() == "true":
    if ENV_JPY_API_TOKEN := os.getenv("JPY_API_TOKEN", None):
        token_parameter = f"?token={ENV_JPY_API_TOKEN}"
elif ENV_AUTHENTICATE_VIA_JUPYTER and ENV_AUTHENTICATE_VIA_JUPYTER.lower() != "false":
    token_parameter = f"?token={ENV_AUTHENTICATE_VIA_JUPYTER}"

# Create Jupyter Shortcut - at runtime since the jupyterhub token is needed
url = f'http://localhost:8092{token_parameter}'
shortcut_metadata = '[Desktop Entry]\nVersion=1.0\nType=Link\nName=Jupyter Notebook\nComment=\nCategories=Development;\nIcon=' + ENV_RESOURCES_PATH + '/icons/jupyter-icon.png\nURL=' + url
call(
    f'printf "{shortcut_metadata}" > {DESKTOP_PATH}/jupyter.desktop',
    shell=True,
)
call(f'chmod +x {DESKTOP_PATH}/jupyter.desktop', shell=True)
call(
    f'printf "{shortcut_metadata}" > /usr/share/applications/jupyter.desktop',
    shell=True,
)
call('chmod +x /usr/share/applications/jupyter.desktop', shell=True) # Make executable

# Create Jupyter Lab Shortcut
url = 'http://localhost:8092' + "/lab" + token_parameter
shortcut_metadata = '[Desktop Entry]\nVersion=1.0\nType=Link\nName=Jupyter Lab\nComment=\nCategories=Development;\nIcon=' + ENV_RESOURCES_PATH + '/icons/jupyterlab-icon.png\nURL=' + url

call(
    f'printf "{shortcut_metadata}" > /usr/share/applications/jupyterlab.desktop',
    shell=True,
)
call('chmod +x /usr/share/applications/jupyterlab.desktop', shell=True) # Make executable

# Configure filebrowser - only if database file does not exist yet (e.g. isn't restored)
if not os.path.exists(f'{HOME}/filebrowser.db'):
    log.info("Initialize filebrowser database.")
    # Init filebrowser configuration - Surpress all output
    call(
        f'filebrowser config init --database={HOME}/filebrowser.db > /dev/null',
        shell=True,
    )

    # Add admin user
    import random, string
    filebrowser_pwd = ''.join(random.sample(string.ascii_lowercase, 20))
    log.info(
        f"Create filebrowser admin with generated password: {filebrowser_pwd}"
    )
    call(
        f'filebrowser users add admin {filebrowser_pwd} --perm.admin=true --database={HOME}/filebrowser.db > /dev/null',
        shell=True,
    )

    # Configure filebrowser
    configure_filebrowser = 'filebrowser config set --root="/" --auth.method=proxy --auth.header=X-Token-Header ' \
                    + ' --branding.files=$RESOURCES_PATH"/filebrowser/" --branding.name="Filebrowser" ' \
                    + ' --branding.disableExternal --signup=false --perm.admin=false --perm.create=false ' \
                    + ' --perm.delete=false --perm.download=true --perm.execute=false ' \
                    + ' --perm.admin=false --perm.create=false --perm.delete=false ' \
                    + ' --perm.modify=false --perm.rename=false --perm.share=false ' \
                    + '  --database=' + HOME + '/filebrowser.db'
    # Port and base url is configured at startup - Surpress all output
    call(f"{configure_filebrowser} > /dev/null", shell=True)

# Tools are started via supervisor, see supervisor.conf