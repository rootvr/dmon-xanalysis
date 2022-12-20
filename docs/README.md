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
    - It must contain the specification of the queryable API of the target application
- The user has to write a YAML workload file:
    - It must contain the list of the days and that of the APIs to attack per-day, describing in this way the entire workload to be generated

### Steps

1. Start of the target application
2. Start of `dmon` (must see the target application)
    - It starts 3 independent workers (threads)
    - The storage worker is responsible for supervising the message brokering and persistence process:
        - It instanciates and manages the connection between the client and the (local or remote) Redis server
        - It asynchronously manages the persistence and publish on Redis channels queues (Redis is natively single-thread and atomic)
        - All data are serialized in JSON format
    - The network worker is responsible for supervising the process of capturing the network interactions of the target application container(s):
        - It instanciates and manages the independent Wireshark-CLI child process
        - It manages the received data, initializes the network payloads and iteracts with the storage thread to perform data serialization, persistence and publication tasks
    - The structure worker is responsible for supervising the process of capturing the data regarding the structure of the target application retrieved from Docker:
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
    - It must contain a list of experiments to execute, also specifying additional configuration parameters (e.g. number of iterations) 

### Steps

1. Start of the target application
2. Start of `dmon` (must see the target application)
3. Start of `dmon-fdriver`
    - It parses the workflow specification YAML file
    - It uses a user-definable root directory as a base directory for the experiments datasets: the directory will be created if it doesn't exist
    - It creates the directory hierarchy for storing all the experiments files
    - Following the workflow specification, it sequencially executes the declared experiments. It waits a user-definable number of seconds between each experiment (the setting is settable in the workflow file) 
    - For each experiment, it executes `dmon-xdriver` as a child process by passing the arguments it needs that are written in the workflow file
4. Start of `dmon-xdriver`
    - It executes `wgen` as a child process by passing the arguments it needs (passed in turn as arguments to `dmon-xdriver` itself)
    - It starts 3 workers (threads). Two of them use a channel for inter-thread communication (in details, the dispatcher and the broker workers use that channel)
    - The wgen-handle worker is responsible for capturing `wgen` output:
        - It captures `wgen` output and it logs it to the standard output: this capture is performed for logging purposes
    - The dispatcher worker is responsible for the serialization of the data payloads into JSON files:
        - It receives the data payloads from the broker worker (thanks to the inter-thread communication channel)
        - It manages the filtering of the data payloads based on a user-definable filter parameter passed as an argument
        - It serializes the data payloads in JSON format and it writes them into multiple JSON files. Each of them have a user-definable maximum number of rows passed as an argument
        - The JSON files are placed inside a user-definable directory (passed as an argument) created at runtime to host the dataset files
    - The broker worker is responsible for supervising the message brokering and the capturing of all the data payloads:
        - It instanciates and manages the connection between the client and the (local or remote) Redis server (the same Redis server used by `dmon`)
        - It starts capturing the data payloads from Redis by subscribing to the channels that contain the data according to the user-definable filter parameter passed as an argument
        - Each captured data payload is forwarded to the inter-thread communication channel (the forwarded data will be managed by the dispatcher worker)

## Uses of multithreading strategies

- `dmon`: the multithreading strategy is used to perform several different data captures at the same time. The microservices-based applications generates all the data simultaneously, so without the use of multithreading we might lose some of the data

- `wgen`: the multithreading strategy is used to simulate multiple requests at the same time made in a single day. In this way we can simulate N users that are concurrently using the microservice-based application according to the workflow that is described in the workload file, and thus we can make a more realistic simulation of a workload

- `dmon-xdriver`: the multithreading strategy is used to handle data acquisition from multiple sources simultaneously. We use one thread to capture `wgen` output and one thread to capture the Redis data at the same time. We also use the multithreading strategy to manage the acquired data: we use a separate thread to write the Redis payloads captured during the test to the JSON files

- `dmon-fdriver`: we do not have multithreading because our purpose here is to organize the test workspace and run `dmon-xdriver` multiple times on separate runs (we wait for one test to complete before starting another) to create the JSON files that we need for analysis
