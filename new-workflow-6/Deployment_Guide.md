# Automated Financial Analysis System: Deployment Guide

## Table of Contents

1.  [**Introduction**](#1-introduction)
    *   1.1. Purpose of This Guide
    *   1.2. About the Deployment Strategy
    *   1.3. What is Docker and Docker Compose?
2.  [**Part 1: Prerequisites & Host Setup**](#part-1-prerequisites--host-setup)
    *   2.1. System Requirements
    *   2.2. Installing Docker Engine on Ubuntu 24.04
    *   2.3. Installing Docker Compose
    *   2.4. Post-Installation Steps for Docker
    *   2.5. Verifying the Installation
3.  [**Part 2: Project Configuration**](#part-2-project-configuration)
    *   3.1. Cloning the Repository
    *   3.2. Understanding the Project Structure
    *   3.3. Environment Variable Configuration (`.env` file)
4.  [**Part 3: The Dockerfile - A Deep Dive**](#part-3-the-dockerfile---a-deep-dive)
    *   4.1. The Anatomy of Our `Dockerfile`
    *   4.2. Base Image and Metadata
    *   4.3. System and Python Dependencies
    *   4.4. The Power of Layer Caching
    *   4.5. Application Code and Final Configuration
5.  [**Part 4: The Docker Compose File - A Deep Dive**](#part-4-the-docker-compose-file---a-deep-dive)
    *   5.1. The Role of `docker-compose.yml`
    *   5.2. Service Breakdown: `financial-analyzer`
    *   5.3. Service Breakdown: `redis` (Our Caching Engine)
    *   5.4. Understanding Volumes and Networks
6.  [**Part 5: Running the Analysis Workflow**](#part-5-running-the-analysis-workflow)
    *   6.1. Building and Running for the First Time
    *   6.2. Performing One-Off Analysis Runs
    *   6.3. Running in the Background (Detached Mode)
    *   6.4. Interacting with a Running Container
    *   6.5. Stopping the Application
7.  [**Part 6: Caching with Redis - How It Works**](#part-6-caching-with-redis---how-it-works)
    *   7.1. Why We Added a Cache
    *   7.2. The Caching Logic in Action
    *   7.3. Benefits of the Caching Layer
8.  [**Part 7: Maintenance and Troubleshooting**](#part-7-maintenance-and-troubleshooting)
    *   8.1. Viewing Application Logs
    *   8.2. Rebuilding the Image After Code Changes
    *   8.3. Managing Docker Resources
9.  [**Conclusion**](#9-conclusion)

---

## 1. Introduction

### 1.1. Purpose of This Guide

Welcome to the official deployment guide for the **Automated Financial Analysis System**. This document provides a comprehensive, step-by-step walkthrough for setting up, configuring, and running the application on an Ubuntu 24.04.1 host using Docker and Docker Compose.

This guide is designed for developers, DevOps engineers, and system administrators who wish to deploy the application in a stable, reproducible, and isolated environment. Beyond simple commands, this document delves into the rationale behind our architectural choices, offering a deep understanding of how each component works.

### 1.2. About the Deployment Strategy

The chosen deployment strategy prioritizes **robustness, portability, and scalability**. By containerizing the application with Docker, we eliminate the "it works on my machine" problem. The entire application, along with its specific Python version and all dependencies, is packaged into a single, portable unit called a Docker image.

We use Docker Compose to define and manage our multi-service application, which includes the main Python analyzer and a Redis database for caching. This approach simplifies the entire deployment process into a few declarative commands, making it incredibly efficient and reliable.

### 1.3. What is Docker and Docker Compose?

*   **Docker** is a platform that enables you to develop, ship, and run applications in containers. A container is a lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries, and settings. It isolates the application from the host system, ensuring consistency across different environments.

*   **Docker Compose** is a tool for defining and running multi-container Docker applications. With a single YAML file (`docker-compose.yml`), you configure all of your application’s services (e.g., your Python app, a database, a caching server). Then, with a single command, you can create and start all the services from your configuration. It's the standard way to manage the lifecycle of containerized applications during development and in many production scenarios.

---

## Part 1: Prerequisites & Host Setup

### 2.1. System Requirements

*   **Operating System:** Ubuntu 24.04.1 LTS (Noble Numbat). While the Dockerized application can run on any OS that supports Docker, these setup instructions are specific to this version of Ubuntu.
*   **Architecture:** `x86_64` / `amd64`.
*   **RAM:** 4GB or more is recommended for smooth operation.
*   **Disk Space:** At least 10GB of free disk space for Docker images, containers, and generated reports.
*   **Internet Connection:** Required for downloading Docker, base images, and financial data from the SEC.

### 2.2. Installing Docker Engine on Ubuntu 24.04

We will install Docker Engine from Docker's official `apt` repository, which is the recommended approach for ensuring we have the latest and most stable version.

**Step 1: Set up Docker's `apt` repository.**
First, update your package index and install the packages required to use an HTTPS repository:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
```

**Step 2: Add Docker’s official GPG key.**
This key verifies the integrity of the packages you are about to download.

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

**Step 3: Add the repository to your `apt` sources.**
This command tells your system where to find the Docker packages.

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**Step 4: Install Docker Engine.**
Finally, update your package index again with the new repository and install Docker Engine, the command-line interface (CLI), and containerd.

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
```

### 2.3. Installing Docker Compose

The `docker-compose-plugin` allows you to use `docker compose` as a direct subcommand of `docker`. This is the modern, integrated way to use Compose.

```bash
sudo apt-get install -y docker-compose-plugin
```

### 2.4. Post-Installation Steps for Docker

By default, the `docker` command requires `sudo`. To run Docker commands without `sudo`, you need to add your user to the `docker` group.

**Step 1: Create the `docker` group (it likely already exists).**

```bash
sudo groupadd docker
```

**Step 2: Add your user to the `docker` group.**
Replace `${USER}` with your actual username.

```bash
sudo usermod -aG docker ${USER}
```

**Step 3: Apply the new group membership.**
You must **log out and log back in** for this change to take effect. Alternatively, you can run the following command to activate the changes for your current terminal session:

```bash
newgrp docker
```

### 2.5. Verifying the Installation

After logging back in, verify that Docker and Docker Compose are installed correctly and can be run without `sudo`.

```bash
docker --version
# Expected output: Docker version 26.x.x, build ...

docker compose version
# Expected output: Docker Compose version v2.x.x
```

You can also run the "hello-world" image to confirm that Docker is fully operational.

```bash
docker run hello-world
```

If you see a message starting with "Hello from Docker!", your installation is successful.

---

## Part 2: Project Configuration

### 3.1. Cloning the Repository

Before you can run the application, you need its source code. Clone the project repository from your version control system (e.g., GitHub).

```bash
git clone <your-repository-url>
cd automated-financial-analysis
```

### 3.2. Understanding the Project Structure

The project has a specific structure that our Docker setup relies on.

```
/
├── .env.example        # Example environment variables
├── docker-compose.yml  # Defines the multi-service Docker environment
├── Dockerfile          # Instructions to build the application image
├── main.py             # The main CLI entry point
├── requirements.txt    # Python dependencies
├── reports/            # Output directory for generated reports (mounted as a volume)
├── logs/               # Output directory for log files (mounted as a volume)
└── src/                # The main application source code package
    └── financial_analysis/
```

### 3.3. Environment Variable Configuration (`.env` file)

Sensitive or environment-specific configuration should not be hardcoded in the application or checked into version control. We manage this using a `.env` file.

**Action:** Copy the example file to create your own local configuration file.

```bash
cp .env.example .env
```

Now, **open the `.env` file** with a text editor and modify the variables.

**`SEC_USER_AGENT`**

This is the most important variable you must change. The U.S. Securities and Exchange Commission (SEC) requires a descriptive `User-Agent` string for all automated traffic to their EDGAR API. This helps them track API usage and contact you if your script is causing issues.

**Change this:**

```
SEC_USER_AGENT="Automated Financial Analysis Project contact@mydomain.com"
```

**To your own information:**

```
SEC_USER_AGENT="Jane Doe Research jane.doe@university.edu"
```

The `docker-compose.yml` file is configured to automatically read this `.env` file and pass these variables into the `financial-analyzer` container's environment at runtime.

---

## Part 3: The Dockerfile - A Deep Dive

### 4.1. The Anatomy of Our `Dockerfile`

The `Dockerfile` is a text document that contains all the commands, in order, needed to build a Docker image. It's like a recipe for creating our application's environment. Let's break down our `Dockerfile` to understand each step.

### 4.2. Base Image and Metadata

```dockerfile
FROM python:3.11-slim-bookworm
LABEL maintainer="CodeNavigator AI"
```

*   `FROM`: This is the first instruction in any `Dockerfile`. It specifies the **base image** to build upon. We use `python:3.11-slim-bookworm`, which is an official Python image.
    *   `3.11`: This guarantees the exact version of Python our application was developed and tested with.
    *   `slim`: This variant is smaller than the full image, resulting in a faster download and a smaller final image size.
    *   `bookworm`: This specifies the underlying Debian OS version, ensuring stability and reproducibility.
*   `LABEL`: This instruction adds metadata to the image. It's useful for organization and identifying the image's purpose or creator.

### 4.3. System and Python Dependencies

```dockerfile
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
WORKDIR /app

RUN apt-get update && apt-get install -y ...
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
```

*   `ENV`: Sets permanent environment variables within the image. `PYTHONUNBUFFERED` ensures that our `print` statements and logs are sent directly to the terminal without being buffered, which is essential for real-time log monitoring. `PYTHONPATH` tells Python where to find our source code modules, enabling clean imports like `from financial_analysis.core.models`.
*   `WORKDIR`: Sets the working directory for all subsequent `RUN`, `CMD`, `COPY`, and `ADD` instructions.
*   `RUN apt-get ...`: This command executes shell commands inside the image. We use it to install system-level libraries that some of our Python packages might need to compile their C extensions.
*   `COPY requirements.txt .`: This copies *only* the `requirements.txt` file into the image.
*   `RUN pip install ...`: This installs all of our Python dependencies.

### 4.4. The Power of Layer Caching

Notice the order: we copy `requirements.txt` and install dependencies *before* we copy the rest of our application code. This is a critical Docker optimization technique.

Docker builds images in **layers**. Each instruction in the `Dockerfile` creates a new layer. When you rebuild an image, Docker checks if the source for a layer has changed. If not, it uses a cached version of that layer instead of re-running the command.

Since our Python dependencies (in `requirements.txt`) change far less frequently than our source code (`.py` files), this structure ensures that the time-consuming `pip install` step is only re-run when we explicitly change a dependency. This makes our development builds significantly faster.

### 4.5. Application Code and Final Configuration

```dockerfile
COPY ./src /app/src
COPY main.py .

EXPOSE 8000
CMD ["python3", "main.py", "--ticker", "AAPL"]
```

*   `COPY . .`: This copies our application source code into the `WORKDIR` of the image.
*   `EXPOSE`: This instruction informs Docker that the container listens on the specified network ports at runtime. It doesn't actually publish the port; it functions as a type of documentation between the person who builds the image and the person who runs it. Our application doesn't have a web server yet, but this prepares it for future enhancements.
*   `CMD`: This provides the **default command** to execute when a container is started from this image. Our default command runs an analysis for the ticker `AAPL`. This command is easily overridden, as we'll see in Part 5.

---

## Part 4: The Docker Compose File - A Deep Dive

### 5.1. The Role of `docker-compose.yml`

If the `Dockerfile` is the recipe for a single dish (our application image), the `docker-compose.yml` file is the recipe for an entire multi-course meal. It describes how multiple services (our Python app, a Redis cache) fit together to form a complete application, defining their runtime configuration, networking, and storage.

### 5.2. Service Breakdown: `financial-analyzer`

This is the main service that runs our Python code.

```yaml
services:
  financial-analyzer:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - redis
    env_file:
      - .env
    volumes:
      - ./src:/app/src
      # ... other volumes
    networks:
      - financial-network
    command: >
      python3 main.py --ticker MSFT
    restart: unless-stopped
```

*   `build`: Tells Compose to build the image from the `Dockerfile` in the current directory (`.`).
*   `depends_on`: This is a crucial directive. It tells Compose that the `financial-analyzer` service depends on the `redis` service. Compose will ensure that the `redis` container is started *before* the `financial-analyzer` container is started.
*   `env_file`: Loads environment variables from the `.env` file we configured earlier.
*   `volumes`: This is one of the most powerful features. It creates a link between a directory on the host machine and a directory inside the container.
    *   `./src:/app/src`: This maps our local `src` directory to the `/app/src` directory in the container. **This means any changes you make to the Python code on your host machine are instantly reflected inside the container, without needing to rebuild the image.** This is fantastic for development.
    *   `./reports:/app/reports`: Any report file generated by the application inside `/app/reports` will be saved directly to the `reports/` directory on your host machine.
    *   `./logs:/app/logs`: Similarly, log files are persisted on the host.
*   `networks`: Attaches this service to our custom `financial-network`.
*   `command`: Overrides the default `CMD` from the `Dockerfile`. In our compose file, the default run is for `MSFT`.
*   `restart: unless-stopped`: A policy that tells Docker to automatically restart this container if it ever crashes, unless it was deliberately stopped.

### 5.3. Service Breakdown: `redis` (Our Caching Engine)

This service provides a high-performance in-memory cache for our application.

```yaml
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped
```

*   `image: redis:7-alpine`: Instead of building from a `Dockerfile`, we are pulling a pre-built, official image directly from Docker Hub. The `alpine` tag indicates it's built on the minimal Alpine Linux distribution, making it very small.
*   `volumes: - redis-data:/data`: This maps a **named volume** called `redis-data` to the `/data` directory inside the Redis container, which is where Redis stores its data. This ensures that our cache is persisted even if we stop and remove the containers.

### 5.4. Understanding Volumes and Networks

*   **Named Volumes (`redis-data`):** These are managed by Docker itself and are the preferred way to persist data generated by containers. They are stored in a dedicated area on the host filesystem managed by Docker.
*   **Bind Mounts (`./src:/app/src`):** These map a specific directory from the host machine into the container. They are ideal for source code and persisting user-facing output like reports.
*   **Custom Networks (`financial-network`):** Creating a custom network allows our containers to communicate with each other using their service names. For example, our Python application can connect to Redis using the hostname `redis`, because they are on the same network. This is more secure and flexible than using legacy links or relying on the default bridge network.

---

## Part 5: Running the Analysis Workflow

### 6.1. Building and Running for the First Time

This command builds the `financial-analyzer` image (if it doesn't exist or if the `Dockerfile` has changed) and starts both the `financial-analyzer` and `redis` services.

```bash
docker compose up --build
```

*   `up`: Brings services up (creates and starts them).
*   `--build`: Forces Docker to build the image before starting the container. You should use this the first time you run, or anytime you change the `Dockerfile` or `requirements.txt`.

You will see the logs from both services stream to your terminal. The application will run the default command from the `docker-compose.yml` file (analyzing `MSFT`).

### 6.2. Performing One-Off Analysis Runs

The most common use case will be to run the analysis for a specific ticker with specific options. We do this by overriding the default command using `docker compose run`.

```bash
docker compose run --rm financial-analyzer python3 main.py <TICKER> [OPTIONS]
```

*   `run`: Executes a one-off command in a new container for a service.
*   `--rm`: Automatically removes the container after the command exits. This is excellent for keeping your system clean from dozens of stopped containers after many runs.
*   `financial-analyzer`: The name of the service we want to run the command in.
*   `python3 main.py ...`: The new command that will be executed inside the container, overriding the default.

**Practical Examples:**

*   **Analyze Apple Inc. and generate both report types:**
    ```bash
    docker compose run --rm financial-analyzer python3 main.py AAPL
    ```

*   **Analyze NVIDIA for the last 3 years and generate only the Excel report:**
    ```bash
    # Note: Our main.py does not yet have a --format option.
    # This example assumes future enhancement. For now, it will always generate both.
    docker compose run --rm financial-analyzer python3 main.py NVDA --years 3
    ```

*   **Analyze Google:**
    ```bash
    docker compose run --rm financial-analyzer python3 main.py GOOGL
    ```

After each command finishes, check your `reports/` directory on your host machine to find the generated `.txt` and `.xlsx` files.

### 6.3. Running in the Background (Detached Mode)

If you wanted to run a service and leave it running in the background (more relevant for a future web API), you would use the `-d` (detach) flag.

```bash
docker compose up -d
```

This starts the services and returns you to the command prompt.

### 6.4. Interacting with a Running Container

If your services are running in the background, you can still execute commands inside them or get a shell.

*   **Execute a new analysis in a running container:**
    ```bash
    # Get the container ID or name first
    docker ps
    
    # Execute the command
    docker exec -it financial-analyzer python3 main.py TSLA
    ```
*   **Open an interactive bash shell for debugging:**
    ```bash
    docker exec -it financial-analyzer /bin/bash
    ```
    You will now be inside the container's shell, at the `/app` directory. You can run `ls`, `cat`, or execute Python scripts manually. Type `exit` to leave.

### 6.5. Stopping the Application

To stop and remove all containers, networks, and volumes defined in your `docker-compose.yml`, use the `down` command.

```bash
docker compose down
```

If you want to stop the services without removing them, use `docker compose stop`.

---

## Part 6: Caching with Redis - How It Works

### 7.1. Why We Added a Cache

Financial data from sources like the SEC doesn't change every second. The facts for a company's 2023 10-K filing will be the same today, tomorrow, and next week. Making a network request to the SEC's API every single time we analyze the same company is inefficient and puts unnecessary load on their servers.

To solve this, we've integrated a **Redis caching layer**. Redis is an extremely fast in-memory key-value store, perfect for this task.

### 7.2. The Caching Logic in Action

Our `SecEdgarProvider` has been upgraded with caching logic. The workflow is now:

1.  When a request for a company's data (e.g., facts for CIK `0000320193`) is made, the provider first generates a unique cache key (e.g., `sec:facts:0000320193`).
2.  It asks the **Redis service** if data exists for this key.
3.  **Cache Hit:** If Redis has the data, it's returned instantly without any network call to the SEC. You will see a `Cache HIT` message in the logs.
4.  **Cache Miss:** If Redis does not have the data, the provider makes the normal network request to the SEC API.
5.  Once the data is successfully fetched from the SEC, it is stored in Redis with the cache key and a 24-hour expiration time. The data is then returned to the application.
6.  The next time the same ticker is analyzed within 24 hours, it will result in a cache hit.

### 7.3. Benefits of the Caching Layer

*   **Performance:** Subsequent analyses of the same company are dramatically faster.
*   **Efficiency:** Reduces the number of API calls to external services, making us a more responsible API consumer.
*   **Resilience:** If the SEC API is temporarily down, we might still be able to run an analysis if the data is in our cache.

---

## Part 7: Maintenance and Troubleshooting

### 8.1. Viewing Application Logs

You can view the real-time logs of all services or a specific service.

*   **Follow logs for all services:**
    ```bash
    docker compose logs -f
    ```
*   **Follow logs for only the Python application:**
    ```bash
    docker compose logs -f financial-analyzer
    ```
    Press `Ctrl+C` to stop following.

### 8.2. Rebuilding the Image After Code Changes

*   If you only change Python code in the `src` directory, you do **not** need to rebuild the image due to our volume mount. Simply re-run the `docker compose run` command.
*   You **must** rebuild the image if you change:
    *   `Dockerfile`
    *   `requirements.txt`
    *   Any file that is `COPY`ed into the image but not mounted as a volume.

    To rebuild, use the `--build` flag:
    ```bash
    docker compose up --build -d
    # or for a one-off run
    docker compose run --build --rm financial-analyzer python3 main.py <TICKER>
    ```

### 8.3. Managing Docker Resources

*   **List running containers:** `docker ps`
*   **List all containers (including stopped):** `docker ps -a`
*   **List images:** `docker images`
*   **Prune unused resources:** To clean up unused containers, networks, and dangling images, you can run:
    ```bash
    docker system prune -a
    ```
    Use with caution, as this will remove all stopped containers and unused data.

---

## 9. Conclusion

You are now equipped with the knowledge to deploy, run, and manage the Automated Financial Analysis System in a professional, containerized environment. This Docker-based approach provides a powerful foundation of stability, reproducibility, and scalability.

By leveraging Docker Compose, we have orchestrated a sophisticated multi-service application with a single, declarative file. The addition of a Redis caching layer elevates the system's performance and efficiency, making it a truly robust tool. This guide provides the blueprint for operating the system effectively and serves as a foundation for any future enhancements or scaling efforts.
