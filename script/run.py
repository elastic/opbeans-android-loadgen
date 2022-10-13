import argparse
import os
import subprocess

from jproperties import Properties


def log(message, *args):
    run_command("echo [APP_BUILDER] - " + message.format(*args))


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
    run_command("git clone https://${GITHUB_USERNAME}:${GITHUB_PASSWORD}@github.com/elastic/opbeans-android.git")
    run_command("git clone https://${GITHUB_USERNAME}:${GITHUB_PASSWORD}@github.com/elastic/apm-agent-android.git")


def build_agent():
    log("Building APM Agent")
    run_command("./gradlew publishToMavenLocal", "./apm-agent-android")


def get_agent_version():
    configs = Properties()
    with open('apm-agent-android/gradle.properties', 'rb') as properties:
        configs.load(properties)

    return configs.get("version").data


def set_opbeans_agent_version(agent_version):
    log("Setting agent version: {}", agent_version)
    with open('opbeans-android/gradle.properties', 'r+b') as properties:
        opbeans_prop = Properties()
        opbeans_prop.load(properties)

        opbeans_prop["agent_version"] = agent_version

        properties.seek(0)
        properties.truncate(0)
        opbeans_prop.store(properties)


def build_binaries(args):
    log("Building APKs")
    command = "./gradlew :app:packageDebugAndroidTest :app:assembleDebug -Pexporter_endpoint={} -Popbeans_endpoint={}".format(
        args.exporterEndpoint, args.opbeansEndpoint)

    if args.exporterAuthToken is not None:
        command = command + " -Pexporter_auth_token={}".format(args.exporterAuthToken)
    if args.opbeansAuthToken is not None:
        command = command + " -Popbeans_auth_token={}".format(args.opbeansAuthToken)

    run_command(command, "./opbeans-android")
    run_command("pwd")
    run_command("ls -l")
    run_command(
        "zip opbeans-android-app.zip opbeans-android/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk opbeans-android/build/outputs/apk/debug/app-debug.apk")


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


def upload_binaries():
    log("Uploading Android binaries")
    run_command("curl -u ${SAUCE_USERNAME}:${SAUCE_ACCESS_KEY} --location \\"
                "--request POST https://api.us-west-1.saucelabs.com/v1/storage/upload \\"
                "--form payload=@\"./opbeans-android-app.zip\" \\"
                "--form 'name=\"opbeans-android-app.zip\"'")


def clean_up():
    log("Cleaning up")
    run_command("rm -rf opbeans-android")
    run_command("rm -rf apm-agent-android")
    run_command("rm opbeans-android-app.zip")


def main():
    args = parse_arguments()
    try:
        fetch_repos()
        build_agent()
        set_opbeans_agent_version(get_agent_version())
        build_binaries(args)
        upload_binaries()
    finally:
        clean_up()


if __name__ == "__main__":
    main()
