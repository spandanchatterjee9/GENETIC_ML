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

## 5. CPU Optimization and Threading in ML Containers

When containerizing Python-based Machine Learning models (such as scikit-learn, numpy, or pandas), it is common to notice high CPU spikes (often exceeding 400% or pinning the host CPU) during startup or prediction.

### Why does this happen?
1. **Concurrency and Multiple Workers**: Uvicorn runs multiple worker processes (e.g., `--workers 4`) to handle concurrent requests. When the container starts, all workers boot simultaneously.
2. **Library Ingestion Overhead**: Heavy mathematical libraries like `scikit-learn`, `scipy`, and `numpy` load underlying C/C++ libraries (such as OpenBLAS, MKL, or OpenMP) on import.
3. **Implicit Multithreading**: By default, libraries like NumPy detect all CPU cores of the host machine and spawn matching worker threads. If your host has 16 logical cores and you run 4 Uvicorn workers, you get up to $4 \times 16 = 64$ threads running concurrently in a single container. This causes high CPU scheduling overhead and context-switching thrashing, spiking the CPU load.

### How to optimize CPU usage:
1. **Restrict Numeric Thread Pools**: Force underlying mathematical libraries to run single-threaded per worker process by setting system environment variables:
   - `OMP_NUM_THREADS=1` (OpenMP)
   - `MKL_NUM_THREADS=1` (Math Kernel Library)
   - `OPENBLAS_NUM_THREADS=1` (OpenBLAS)
   - `VECLIB_MAXIMUM_THREADS=1` (Vector Library)
   - `NUMEXPR_NUM_THREADS=1` (NumExpr)
2. **Reduce Uvicorn Workers**: Set Uvicorn to run with 2 workers instead of 4. Since FastAPI is asynchronous, 2 workers are more than sufficient to handle high concurrency while cutting memory and boot CPU footprints in half.

