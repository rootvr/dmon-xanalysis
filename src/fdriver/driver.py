import yaml
import time
import pathlib
import subprocess
import logging
import os
import datetime
import sys


class Driver:
    def __init__(self, args):
        self.logger = logging.getLogger("fdriver")
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.terminator = ""
        ch.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(name)s %(levelname)s %(message)s")
        ch.setFormatter(fmt)
        self.logger.addHandler(ch)
        self.args = args
        with open(self.args.workflow_file) as w:
            self.workflow = yaml.load(w, Loader=yaml.FullLoader)
        self.validate()

    def validate(self):
        assert type(self.workflow["app"]) == str
        for test in self.workflow["flow"]:
            assert type(test["iter"]) == int and test["iter"] > 0
            assert type(test["name"]) == str
            assert type(test["sleep"]) == int and test["sleep"] > 0
            assert type(test["xdriver"]) == dict
            assert type(test["xdriver"]["filter"]) == str
            assert type(test["xdriver"]["rows"]) == int
            assert type(test["xdriver"]["redis"]) == dict
            assert type(test["xdriver"]["redis"]["ip"]) == str
            assert type(test["xdriver"]["redis"]["port"]) == int
            assert type(test["xdriver"]["wgen"]) == dict
            assert type(test["xdriver"]["wgen"]["workload"]) == str
            test["xdriver"]["wgen"]["workload"] = (
                pathlib.Path(self.args.workflow_file).parent
                / pathlib.Path(test["xdriver"]["wgen"]["workload"])
            ).resolve(strict=True)
            assert type(test["xdriver"]["wgen"]["apispec"]) == str
            test["xdriver"]["wgen"]["apispec"] = (
                pathlib.Path(self.args.workflow_file).parent
                / pathlib.Path(test["xdriver"]["wgen"]["apispec"])
            ).resolve(strict=True)
            assert type(test["xdriver"]["wgen"]["day"]) == str

    @staticmethod
    def dtime():
        return f"{datetime.datetime.now():%d%m%y-%H%M%S}-"

    @staticmethod
    def cmd_build(
        logdirname,
        logmaxrows,
        filter,
        redisipv4,
        redisport,
        workloadfile,
        apispecfile,
        daylength,
    ):
        return f"dmon-xdriver \
        --log-dirname {logdirname} \
        --log-maxrows {logmaxrows} \
        --filter {filter} \
        --redis-ipv4 {redisipv4} \
        --redis-port {redisport} \
        --wgen-workload-file {workloadfile} \
        --wgen-apispec-file {apispecfile} \
        --wgen-day-length {daylength} \
        -c \
        "

    def copy_wgen(self):
        workload_cmd = f"cp -f {self.workflow['flow'][self.curr_test]['xdriver']['wgen']['workload']} {self.test_dir}"
        apispec_cmd = f"cp -f {self.workflow['flow'][self.curr_test]['xdriver']['wgen']['apispec']} {self.test_dir}"
        os.system(workload_cmd)
        os.system(apispec_cmd)

    def copy_flow(self):
        workflow_cmd = f"cp -f {self.args.workflow_file} {self.root_dir.parent}"
        os.system(workflow_cmd)

    # def execute(self, command):
    #     with subprocess.Popen(
    #         command, stdout=subprocess.PIPE, universal_newlines=True
    #     ) as p:
    #         if p.stdout != None:
    #             for line in iter(p.stdout.readline, ""):
    #                 yield line

    def run(self):
        self.root_dir = (
            pathlib.Path(f"{self.args.root_dir}")
            .joinpath(f"{self.dtime()}{self.workflow['app']}")
            .joinpath("data")
        )
        self.root_dir.mkdir(parents=True, exist_ok=True)
        # tt = len(self.workflow['flow'])
        tt = 0
        for test in self.workflow["flow"]:
            tt += test["iter"]
        ii = 0
        for idx, test in enumerate(self.workflow["flow"]):
            self.curr_test = idx
            self.test_dir = self.root_dir.joinpath(
                f"{self.dtime()}{idx}-{test['name']}"
            )
            for iter in range(test["iter"]):
                ii += 1
                self.run_dir = self.test_dir.joinpath(
                    f"{iter}-{test['xdriver']['wgen']['day']}"
                )

                # for output in self.execute(
                #         self.cmd_build(
                #             self.run_dir,
                #             "s",
                #             test["xdriver"]["filter"],
                #             test["xdriver"]["redis"]["ip"],
                #             test["xdriver"]["redis"]["port"],
                #             test["xdriver"]["wgen"]["workload"],
                #             test["xdriver"]["wgen"]["apispec"],
                #             test["xdriver"]["wgen"]["day"],
                #         ).split(),
                #     ):
                #     print(output, end='')

                with subprocess.Popen(
                    self.cmd_build(
                        self.run_dir,
                        test["xdriver"]["rows"],
                        test["xdriver"]["filter"],
                        test["xdriver"]["redis"]["ip"],
                        test["xdriver"]["redis"]["port"],
                        test["xdriver"]["wgen"]["workload"],
                        test["xdriver"]["wgen"]["apispec"],
                        test["xdriver"]["wgen"]["day"],
                    ).split(),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ) as p:
                    if p.stdout != None:
                        for line in p.stdout:
                            sys.stdout.write("\x1b[2K\r")
                            self.logger.info(line.decode())
                            self.logger.info(
                                f"Running test {idx+1}/{len(self.workflow['flow'])}, epoch {iter+1}/{test['iter']}\r"
                            )

                time.sleep(test["sleep"])
            self.copy_wgen()
        self.copy_flow()
