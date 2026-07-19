# Docker Concepts: Single-Container vs. Multi-Container (Microservices) Architectures

This document explains the core concepts of containerization, compares unified single-container setups with multi-container (microservice) architectures, and breaks down the exact settings, networking, and volumes defined in your Docker Compose structures.

---

## 1. Resolving the Container Name Query
In your previous `docker-compose.yml`, the container was named `alzheimers-flask` and had the environment variable `FLASK_ENV=production`. 
- **Why it was there**: These were legacy settings from the original Flask application.
- **How we fixed it**: We have updated `docker-compose.yml` to use `container_name: alzheimers-fastapi` and removed the obsolete `FLASK_ENV` variable. The container now reflects our FastAPI architecture.

---

## 2. Monolithic vs. Microservices Container Architectures

Containers can be structured in two ways depending on scaling and development needs:

### A. Single-Container (Unified) Architecture (Our Current Setup)
In our current `GENETIC_ML` setup, we run a single container.
- **How it works**: A single Docker container hosts our FastAPI backend, which also serves the frontend views (via Jinja2 templates and mounted static files) and runs the Machine Learning models directly in memory.
- **When to use it**: Ideal for simpler applications, proof-of-concepts, or ML demonstration projects. It simplifies deployment (only one container to build and run) and reduces memory overhead since there are no inter-service networking hops.

### B. Multi-Container (Microservice) Architecture (Your Snippet Setup)
In a microservices setup, you separate responsibilities into dedicated containers (e.g., Database, Backend API, Frontend Server).
- **How it works**: Each tier runs in its own isolated OS container, communicating over virtual bridge networks.
- **When to use it**: Standard for production enterprise systems. It allows you to scale components independently (e.g., run 10 instances of the frontend, 5 of the backend, and 1 database cluster) and deploy updates to one layer without taking down the others.

---

## 3. Deconstructing Your Docker Compose Snippet

Let's break down the exact meaning of every concept and keyword in your example Compose configuration.

### Service 1: `mariadb` (The Database)
```yaml
mariadb:
    image: "bitnami/mariadb:latest"
    environment:
        - MARIADB_ROOT_PASSWORD=root
        - MARIADB_USER=maria
        - MARIADB_PASSWORD=maria
        - MARIADB_DATABASE=mcube_sizing
    restart: always
    ports:
        - 3307:3306
    volumes:
        - maria_data:/bitnami/mariadb
        - ./config/sql:/docker-entrypoint-initdb.d
    networks:
        - mcube-sizing-net
```
- **`image`**: Instead of building a custom image from a local Dockerfile, this tells Docker to download a pre-built official image (`bitnami/mariadb:latest`) from Docker Hub.
- **`environment`**: Passes configuration parameters into the container on startup. The MariaDB database engine reads these variables to create the database (`mcube_sizing`) and set up usernames and credentials automatically.
- **`restart: always`**: If the database crashes or the host system restarts, Docker daemon automatically boots the container back up.
- **`ports: 3307:3306`**: Port Mapping in format **`HOST:CONTAINER`**. MariaDB inside the container listens on the standard MySQL port `3306`. Docker maps it to port `3307` on your actual host computer, preventing conflicts with any local MySQL databases already running on `3306`.
- **`volumes`**:
  - `maria_data:/bitnami/mariadb`: Maps a named volume (`maria_data`) to the database data directory inside the container. This ensures your database records persist even if the container is deleted or rebuilt.
  - `./config/sql:/docker-entrypoint-initdb.d`: Maps a local directory containing SQL scripts to the container's init folder. When the database boots for the first time, it automatically runs any `.sql` files found here to create tables and seed mock data.
- **`networks`**: Connects this database to the virtual bridge network `mcube-sizing-net` so other services in the same network can access it.

---

### Service 2: `backend` (The REST API)
```yaml
backend:
    build:
        context: ./backend
        dockerfile: Dockerfile
    restart: always
    ports:
        - 8001:8000
    networks:
        - mcube-sizing-net
    volumes:
        - ./config/json/config.json:/app/config.json
    environment:
        - AI_SERVICE_HOST=host.docker.internal
    extra_hosts:
        - "host.docker.internal:host-gateway"
    depends_on:
        - mariadb
```
- **`build`**:
  - `context`: Points to the folder `./backend` containing the source code.
  - `dockerfile`: Tells Docker to build a custom container image using the `Dockerfile` inside that directory.
- **`ports: 8001:8000`**: Maps port `8000` inside the container (where FastAPI/Uvicorn is running) to port `8001` on your host machine.
- **`volumes: ./config/json/config.json:/app/config.json`**: Mounts a single configuration JSON file from your host system directly into the container. If you modify this file on your host, the container sees the updates in real-time without needing a rebuild.
- **`extra_hosts` & `host.docker.internal:host-gateway`**: Instructs Docker to map the hostname `host.docker.internal` to the host machine's IP address. This allows the backend inside the container to connect to other applications running directly on your local system (outside of Docker) using that hostname.
- **`depends_on`**: Dictates the startup order. Docker ensures the `mariadb` container is started before booting up the `backend` container.

---

### Service 3: `frontend` (The Presentation Layer)
```yaml
frontend:
    build:
        context: ./frontend
        dockerfile: Dockerfile
    restart: always
    ports:
        - 3000:3000
    environment:
        - BACKEND_URL=http://backend:8000
        - NEXTAUTH_URL=http://localhost:3000
    networks:
        - mcube-sizing-net
    depends_on:
        - backend
```
- **`BACKEND_URL=http://backend:8000`**: Notice the URL hostname is `backend`! In Docker, containers on the same network use **automatic service discovery**. The frontend container does not need to know the IP address of the backend; it can just call the service name `backend` directly on the internal container port (`8000`).

---

## 4. Shared Resources Section

### A. Named Volumes
```yaml
volumes:
    maria_data:
        name: sizing_maria_data
```
Volumes are directory paths managed directly by Docker outside of the container's temporary read-write layers.
- **Named vs. Bind Mounts**: Mapping directories by absolute/relative local paths (like `./config/sql`) is a **bind mount**. Creating a declared volume (like `maria_data`) is a **named volume** managed by Docker. Named volumes are faster, isolated from host OS permissions, and backed up easily.

### B. Bridge Networks
```yaml
networks:
    mcube-sizing-net:
        driver: bridge
        name: mcube-sizing-net
```
- **`driver: bridge`**: The default networking mode. Docker creates an isolated virtual local network interface card (NIC) on your host. Only containers attached to this virtual network can communicate with one another, shielding them from external network scans while allowing seamless inter-service discovery.

---

## 5. Container Resource Allocation: CPU vs. RAM (Memory Usage)

When running containerized applications, Docker Desktop monitors two distinct host hardware resources: **CPU Usage** and **Container Memory Usage (RAM)**. Understanding these metrics is vital for debugging resource allocation differences between projects.

### A. Core Differences: CPU vs. RAM in Containers

1. **CPU Usage (Processor)**:
   - **What it is**: The percentage of processor cycles consumed by active threads *at any given moment*. 
   - **Characteristics**: CPU usage is highly dynamic. It spikes during server startups, code compilation, and model predictions, but drops to near 0% when the server is idle.
2. **Memory Usage (RAM)**:
   - **What it is**: The volume of random-access memory (RAM) allocated and held by the running processes *across all containers in the stack*.
   - **Characteristics**: RAM usage is persistent and static. Once the application loads its libraries, imports dependencies, and reads model files into memory, it retains that RAM allocation to handle requests. It remains high even when the server is idle.

---

### B. Analyzing the Memory Footprint: `genetic_ml` (~800MB) vs. `mcube-sizing-estimator` (~190MB)

You will notice that the `genetic_ml` container stack consumes around **793 MB** of RAM on start, whereas the `mcube-sizing-estimator` stack uses only **189 MB** of RAM. This significant difference is caused by the following architectural factors:

#### 1. Machine Learning Framework Imports (The Library Footprint)
- **`genetic_ml`**: To run standard scaling preprocessing and Random Forest prediction logic, the python backend must import heavy scientific frameworks: `scikit-learn`, `pandas`, `scipy`, and `numpy`. Loading these libraries into a Python virtual machine instantly consumes about **150MB–200MB** of RAM per process due to compiled C-extensions.
- **`mcube-sizing-estimator`**: If an application performs calculations using raw Python math modules, custom rules, or a lightweight parser instead of importing the entire `scikit-learn` stack, its basic library load footprint is minimal (typically under **30MB** of RAM).

#### 2. Model Deserialization (In-Memory Pickles)
- **`genetic_ml`**: At startup, the backend deserializes `rf_alzheimers_model.pkl` (a Random Forest containing multiple decision trees with split nodes) and `scaler.pkl`. These serialized objects must reside fully in RAM to serve predictions at sub-millisecond latencies.
- **`mcube-sizing-estimator`**: Does not load a heavy scikit-learn ensemble pickle, keeping in-memory object allocations small.

#### 3. Worker Process Multiplication (Process-Level Isolation)
Uvicorn runs multiple worker processes (e.g. `--workers 2` or `4`) to support concurrency. Because Python uses process-level isolation for workers:
- **Each worker process spawns a separate memory space**.
- Each process independently imports Python interpreter packages (`scikit-learn`, `pandas`, `numpy`) and loads its own copy of the serialized Random Forest model into RAM.
- If one worker process requires **250MB** of RAM, running 2 workers uses **500MB** of RAM, and running 4 workers uses **1.0GB** of RAM.

#### 4. Stack Composition (Total Service Count)
Docker Desktop displays the **total aggregated RAM usage** of all services declared in your `docker-compose.yml`:
- **`mcube-sizing-estimator`**: Runs a single container (FastAPI backend + lightweight SQLite file database).
- **`genetic_ml`**: Runs a full multi-container stack:
  1. `genetic-ml-backend` (FastAPI + SciPy/SKLearn + Model + 2 Workers) $\approx 500\text{MB}$
  2. `genetic-ml-db` (MariaDB SQL container allocating internal buffer pools and connection caches) $\approx 150\text{MB}$
  3. `genetic-ml-frontend` (Nginx proxy container serving HTML/static assets) $\approx 15\text{MB}$
  - **Combined Stack Memory**: $\approx 793\text{MB}$
