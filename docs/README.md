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
- It is used to perform a single experiment and to build the dataset (JSON file) by driving the entire capture process

### Workflow driver (`dmon-fdriver`)

- It must find a `dmon-xdriver` executable on the host machine
- It is used to perform a sequence of experiments by driving the experiment driver following a workflow specification
- The user has to write a YAML workflow file:
    - It must contain a list of experiments to execute, also specifying additional configuration parameters (e.g. number of iterations) 

### Steps

1. `dmon-fdriver` todo
2. `dmon-xdriver` todo
