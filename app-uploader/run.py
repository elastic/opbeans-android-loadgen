import argparse
import os
import subprocess
from jproperties import Properties


def log(message, *args):
    print("[APP_BUILDER] - " + message.format(*args))


def run_build_command(command, from_build_dir=''):
    run_command(command, "./build" + from_build_dir)


def run_command(command, from_dir=os.getcwd()):
    print("Running command: {}".format(command))
    with subprocess.Popen(command, stdout=subprocess.PIPE, cwd=from_dir, bufsize=1,
                          universal_newlines=True, shell=True) as p:
        for line in p.stdout:
            print(line, end='')

    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)


def fetch_repos():
    log("Fetching repos")
    run_build_command("git clone https://github.com/elastic/opbeans-android.git")
    run_build_command("git clone https://github.com/elastic/apm-agent-android.git")


def build_agent():
    log("Building APM Agent")
    run_build_command("./gradlew publishToMavenLocal", "/apm-agent-android")


def get_app_file_name():
    configs = Properties()
    with open('app_file_names.properties', 'rb') as properties:
        configs.load(properties)

    data = configs.get(os.environ['CLUSTER_NAME']).data
    log("Using app name: '{}'", data)
    return data


def get_agent_version():
    configs = Properties()
    with open('build/apm-agent-android/gradle.properties', 'rb') as properties:
        configs.load(properties)

    return configs.get("version").data


def set_opbeans_agent_version(agent_version):
    log("Setting agent version: {}", agent_version)
    with open('build/opbeans-android/gradle.properties', 'r+b') as properties:
        opbeans_prop = Properties()
        opbeans_prop.load(properties)

        opbeans_prop["agent_version"] = agent_version

        properties.seek(0)
        properties.truncate(0)
        opbeans_prop.store(properties)


def build_binaries(app_file_name, args):
    log("Building APKs")
    endpoint = args.opbeansEndpoint
    if not endpoint.startswith('http'):
        endpoint = "https://" + endpoint
    log("Using opbeans endpoint: {}", endpoint)
    command = "./gradlew :app:packageDebugAndroidTest :app:assembleDebug -Pexporter_endpoint={} -Popbeans_endpoint={}".format(
        args.exporterEndpoint, endpoint)

    if args.exporterAuthToken is not None:
        command = command + " -Pexporter_auth_token={}".format(args.exporterAuthToken)
    if args.opbeansAuthToken is not None:
        command = command + " -Popbeans_auth_token={}".format(args.opbeansAuthToken)

    run_build_command(command, "/opbeans-android")
    run_build_command(
        "cp opbeans-android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk ./testApp.apk")
    run_build_command("cp opbeans-android/app/build/outputs/apk/debug/app-debug.apk ./app.apk")
    run_build_command("zip -j {} testApp.apk app.apk".format(app_file_name))


def none_or_str(value):
    if value == 'None':
        return None
    return value


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exporter-endpoint', dest='exporterEndpoint')
    parser.add_argument('--exporter-auth-token', dest='exporterAuthToken', type=none_or_str,
                        default=None)
    parser.add_argument('--opbeans-endpoint', dest='opbeansEndpoint')
    parser.add_argument('--opbeans-auth-token', dest='opbeansAuthToken', type=none_or_str,
                        default=None)
    return parser.parse_args()


def upload_binaries_to_saucelabs(app_file_name):
    log("Uploading Android binaries")
    run_build_command("curl -u $SAUCE_USERNAME:$SAUCE_ACCESS_KEY --location \\"
                      "--request POST https://api.us-west-1.saucelabs.com/v1/storage/upload \\"
                      "--form payload=@\"./{}\" \\"
                      "--form 'name=\"{}\"'".format(app_file_name, app_file_name))


def upload_app_to_firebase():
    log("Uploading to Firebase")
    run_build_command("./gradlew appDistributionUploadDebug -Pfirebase_release_notes=$CLUSTER_NAME", "/opbeans-android")


def clean_up():
    log("Cleaning up")
    run_command("rm -rf build")


def create_build_dir():
    log("Creating build dir")
    run_command("mkdir build")


def main():
    args = parse_arguments()
    try:
        create_build_dir()
        fetch_repos()
        build_agent()
        set_opbeans_agent_version(get_agent_version())
        app_file_name = get_app_file_name()
        build_binaries(app_file_name, args)
        upload_binaries_to_saucelabs(app_file_name)
        upload_app_to_firebase()
    finally:
        clean_up()


if __name__ == "__main__":
    main()
