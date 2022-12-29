## Capture process description (focus on concurrency)

### Target application

- It must be powered by Docker
- It can be a monolithic or microservice-based one
- All its containers must run on the host machine
- It must be reachable through the Docker socket (launch param: `-v /var/run/docker.sock:/var/run/docker.sock`)
- It must unify its network with the one of the host machine (launch param: `--network=host`)
- It must expose an queryable API (to be attacked by the workload generator)

### Monitoring system (`dmon`)

- It can be run as a local executable or as a Docker container
- In case of local executable: Redis server and Wireshark-CLI are required
- The Docker container version contains Redis and Wireshark-CLI, but the Redis server could be located on a remote Docker container
- It must run on the host machine

### Workload generator (`wgen`)

- It must run on the host machine
- It must be a local executable
- The user has to write a YAML API specification file:
    - It must contain the specification of the queryable API of the target application (example)
    ```yaml
    # app name
    name: app_name API
    # base URL
    baseUrl: http://localhost:8080
    # API endpoints list
    api:
      # endpoint name
      index:
        # endpoint relative URL
        relativeUrl: /
        # endpoint HTTP method
        method: GET
      catalogue:
        relativeUrl: /catalogue
        method: GET
    ```
- The user has to write a YAML workload file:
    - It must contain the list of the days and that of the APIs to attack per-day, describing in this way the entire workload to be generated (example)
    ```yaml
    workload:
    # days list
    - day:
      # target API endpoint name
      index:
        # [attack rate * attack timer]
        # attack rate (number of requests)
        rate: 5
        # attack timer (time unit for number of requests) 
        # (seconds: `s`, minutes: `m`, hours: `h`)
        unit: h
      catalogue:
        rate: 100
        unit: m
    - day:
      index:
        rate: 500
        unit: s
    ```

### Steps

1. Start of the target application
2. Start of `dmon` (must see the target application)
    - It starts 3 independent workers (threads)
    - The `storage` worker is responsible for supervising the message brokering and persistence process:
        - It instanciates and manages the connection between the client and the (local or remote) Redis server
        - It asynchronously manages the persistence and publish on Redis channels queues (Redis is natively single-thread and atomic)
        - All data are serialized in JSON format
    - The `network` worker is responsible for supervising the process of capturing the network interactions of the target application container(s):
        - It instanciates and manages the independent Wireshark-CLI child process
        - It manages the received data, initializes the network payloads and iteracts with the storage thread to perform data serialization, persistence and publication tasks
    - The `structure` worker is responsible for supervising the process of capturing the data regarding the structure of the target application retrieved from Docker:
        - It communicates with the Docker server (through the Docker socket) to retrieve these data
        - The data regard the host machine, the virtual Docker networks and containers
        - It manages the received data, initializes the structure payloads and iteracts with the storage thread to perform data serialization, persistence and publication tasks
        - It uses a user-definable timer to poll data retrieving
3. Start of `wgen` (must see the target application)
    - It parses the API specification and the workload YAML files
    - A user-definable day length (in seconds, minutes or hours) is used to perform the simulation/compression of the workload
    - Following the workload specification, it sequencially executes the declared days and for the same day it simultaneously executes the declared API attacks (for each day)
    - It creates a separated worker (thread) for each API attack, simulating in this way the action of multiple concurrent attackers

## Experimentation process description

### Experiment driver (`dmon-xdriver`)

- It must run on the host machine
- It must be a local executable
- It must find a `wgen` executable on the host machine
- It must find an online instance of the Redis server (the same that `dmon` uses, could be a local server or a remote Docker-powered one)
- It is used to perform a single experiment and to build the dataset (JSON files) by driving the entire capture process

### Workflow driver (`dmon-fdriver`)

- It must find a `dmon-xdriver` executable on the host machine
- It is used to perform a sequence of experiments by driving the experiment driver following a workflow specification
- The user has to write a YAML workflow file:
    - It must contain a list of experiments to execute, also specifying additional configuration parameters (e.g. number of iterations) (example) 
    ```yaml
    # app name
    app: robotshop
    flow:
      # test name
      - name: t1mx10
        # number of iterations
        iter: 10
        # number of seconds between iterations (sleep)
        sleep: 3
        # dmon-xdriver parameters
        xdriver:
          # max number of rows for each result file
          rows: 1000
          # payload type filter (network, structure or none)
          filter: network
          # redis server location
          redis:
            ip: 0.0.0.0
            port: 6379
        # wgen parameters
          wgen:
            # path to the workload file
            workload: ./robotshop-t1mx10-workload.yml
            # path to the apispec file
            apispec: ../template/robotshop/apispec.yml
            # day length (seconds: `s`, minutes: `m`, hours: `h`)
            day: 1m
      - name: t5mx10
        iter: 10
        sleep: 3
        xdriver:
          rows: 1000
          filter: network
          redis:
            ip: 0.0.0.0
            port: 6379
          wgen:
            workload: ./robotshop-t5mx10-workload.yml
            apispec: ../template/robotshop/apispec.yml
            day: 5m
    ```

### Steps

1. Start of the target application
2. Start of `dmon` (must see the target application)
3. Start of `dmon-fdriver`
    - It expects as parameters the YAML workflow specification file and a filesystem path (where it will store all the results of the experiment(s))
    - It creates the following directory hierarchy (example):
    ```console
    dmon-xanalysis/test/141222-152519-robotshop
    ├── data
    │  ├── 141222-152519-0-t1mx10
    │  │  ├── 0-1m
    │  │  │  ├── 0.net.gen.json
    │  │  │  ├── 0.struct.cont.json
    │  │  │  ├── 0.struct.host.json
    │  │  │  ├── 0.struct.net.json
    │  │  │  └── ...
    │  │  ├── 1-1m
    │  │  │  └── ...
    │  │  ├── ...
    │  │  ├── apispec.yml
    │  │  └── robotshop-t1mx10-workload.yml
    │  ├── 141222-153551-1-t5mx10
    │  │  ├── 0-5m
    │  │  │  ├── 0.net.gen.json
    │  │  │  ├── 0.struct.cont.json
    │  │  │  ├── 0.struct.host.json
    │  │  │  ├── 0.struct.net.json
    │  │  │  ├── 1.net.gen.json
    │  │  │  └── ...
    │  │  ├── 1-5m
    │  │  │  └── ...
    │  │  ├── ...
    │  │  ├── apispec.yml
    │  │  └── robotshop-t5mx10-workload.yml
    │  └── ...
    ├── robotshop-t1mx10-t5mx10-analysis.html
    ├── robotshop-t1mx10-t5mx10-analysis.ipynb
    └── robotshop-t1mx10-t5mx10-workflow.yml
    ```
    - For each declared experiment, it launches `dmon-xdriver` as a child process passing the respective experiment configuration to it
4. Start of `dmon-xdriver` (child process, for each declared experiment)
    - It launches `wgen` as a child process passing the correct arguments to it
    - It starts 3 workers (threads)
    - The `wgen-handle` group of workers is responsible for capturing `wgen` output:
        - The threads use the `wgen` communication buffer to log its output from stdout and stderr file descriptors
    - The `broker` worker is responsible for supervising the message brokering and capturing all the data payloads:
        - It instanciates and manages the connection between the client and the (local or remote) Redis server
        - It acts as a Redis client, capturing all the data payloads by subscribing to the correct Redis channel (based on the `filter` parameter declared for experiments in the workflow YAML file)
        - Each captured data is sent to the writer worker for serialization
    - The `writer` worker is responsible for serializing the data in JSON and writing the results to the filesystem:
        - It dispatches the data serialization based on the payload type (`network`, `structure` or `none`) and layout (`general`, `host`, `container`, `network`)
        - It serializes the data payloads in JSON format and it writes them into multiple JSON files (based on the `rows` parameter declared for experiments in the workflow YAML file)
