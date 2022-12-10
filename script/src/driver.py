import meta
import os
import sys
import subprocess

from fs import read_yaml_from_file, check_dir_exists, create_dir


class Driver:
    def __init__(self, args):
        self.config_data = read_yaml_from_file(args.config_file)
        self.xdriver_log_maxrows = self.config_data[meta.XDRIVER_KEY][
            meta.XDRIVER_LOG_MAXROWS_KEY
        ]
        self.xdriver_filter = "network"
        self.redis_ipv4 = self.config_data[meta.REDIS_KEY][meta.REDIS_IPV4_KEY]
        self.redis_port = self.config_data[meta.REDIS_KEY][meta.REDIS_PORT_KEY]
        self.wgen_apispec_file = self.config_data[meta.WGEN_KEY][
            meta.WGEN_APISPEC_FILE_KEY
        ]
        self.tests_data = {}

    def run(self):
        self.create_env()
        for duration in self.tests_data.keys():
            for i, test in enumerate(self.tests_data[duration], 1):
                print(f"-- Running test {i} for duration {duration} --")
                self.xdriver_run(duration, test["dir_path"], test["workload_file"])

    def xdriver_run(self, day_length: str, dir_path: str, workload_file: str):
        xdriver_command = f"""
            dmon-xdriver --log-dirname {dir_path}
                         --log-maxrows {self.xdriver_log_maxrows}
                         --filter {self.xdriver_filter}
                         --redis-ipv4 {self.redis_ipv4}
                         --redis-port {self.redis_port}
                         --wgen-workload-file {workload_file}
                         --wgen-apispec-file {self.wgen_apispec_file}
                         --wgen-day-length {day_length}
        """

        for output in self.execute(xdriver_command.split()):
            print(output, end="")

    def execute(self, command):
        popen = subprocess.Popen(
            command, stdout=subprocess.PIPE, universal_newlines=True
        )
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        print(f"return_code: {popen.wait()}")

    def create_env(self) -> None:
        app = self.config_data[meta.APP_KEY]
        data_dir = self.config_data[meta.TEST_KEY][meta.TEST_DATA_DIR_KEY]
        test_durations = self.config_data[meta.TEST_KEY][meta.TEST_DURATIONS_KEY]
        jupyter_dir = self.config_data[meta.TEST_KEY][meta.TEST_JUPYTER_DIR_KEY]
        test_repetitions = self.config_data[meta.TEST_KEY][meta.TEST_REPETITIONS_KEY]

        if not check_dir_exists(os.path.join(meta.BASE_DIR)):
            create_dir(meta.BASE_DIR)

        if check_dir_exists(os.path.join(meta.BASE_DIR, app)):
            print(meta.DATA_DIR_EXISTS_ERROR)
            sys.exit(1)

        create_dir(os.path.join(meta.BASE_DIR, app))
        create_dir(os.path.join(meta.BASE_DIR, app, data_dir))
        create_dir(os.path.join(meta.BASE_DIR, app, jupyter_dir))

        for d in test_durations:
            for i in range(1, test_repetitions + 1):
                dir_name = d + f"_t{i}"
                dir_path = os.path.join(meta.BASE_DIR, app, data_dir, dir_name)
                test_workload_file = self.config_data[meta.WGEN_KEY][d][
                    meta.WGEN_WORKLOAD_FILE_KEY
                ]

                self.set_test_data(d, dir_path, test_workload_file)

    def set_test_data(self, test: str, dir_path: str, workload_file: str):
        d = {"dir_path": dir_path, "workload_file": workload_file}
        if test not in self.tests_data:
            self.tests_data[test] = [d]
        else:
            self.tests_data[test].append(d)
