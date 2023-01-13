import json
import os
import subprocess
from jproperties import Properties


def run_command(command, from_dir=os.getcwd()):
    log("Running command: {}", command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=from_dir, universal_newlines=True, shell=True)
    output, error = process.communicate()
    if error:
        raise error

    return output


def run_command_stdout(command, from_dir=os.getcwd()):
    print("Running command: {}".format(command))
    with subprocess.Popen(command, stdout=subprocess.PIPE, cwd=from_dir, bufsize=1,
                          universal_newlines=True, shell=True) as p:
        for line in p.stdout:
            print(line, end='')

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)


def run_build_command(command, from_build_dir=''):
    return run_command(command, "./build" + from_build_dir)


def log(message, *args):
    print("[LOAD_GENERATOR] - " + message.format(*args))


def get_latest_app_id(app_file_name):
    result = run_command(
        "curl -u $SAUCE_USERNAME:$SAUCE_ACCESS_KEY --location \\"
        "--request GET 'https://api.us-west-1.saucelabs.com/v1/storage/files?name={}&per_page=1' | json_pp".format(
            app_file_name))

    data = json.loads(result)
    items = data['items']
    latest = items[0]
    return latest['id']


def download_app(app_id):
    log("Dowloading app with id: {}", app_id)
    run_build_command(
        "curl -u $SAUCE_USERNAME:$SAUCE_ACCESS_KEY --location \\"
        "--request GET 'https://api.us-west-1.saucelabs.com/v1/storage/download/{}' \\"
        "--output app.zip".format(app_id))

    run_build_command("unzip app.zip")


def create_build_dir():
    run_command("mkdir build")


def clean_up():
    log("Cleaning up")
    run_command("rm -rf build")


def get_app_file_name():
    configs = Properties()
    with open('app_file_names.properties', 'rb') as properties:
        configs.load(properties)

    data = configs.get(os.environ['CLUSTER_NAME']).data
    log("Using app name: '{}'", data)
    return data


def run_espresso():
    log("Running espresso tests")
    run_command_stdout("saucectl run")


def main():
    app_id = get_latest_app_id(get_app_file_name())
    try:
        create_build_dir()
        download_app(app_id)
        run_espresso()
    finally:
        clean_up()


if __name__ == "__main__":
    main()
