# Difference between `docker compose up --build -d` and  
`docker compose run --build --rm financial-analyzer python3 main.py <TICKER>`

## `docker compose up --build -d`

This command builds (if needed) and starts **all** services defined in your `docker-compose.yml`, then leaves them running in the background (detached mode).

  
- Builds or rebuilds images for every service before starting containers.  
- Creates containers, networks, and volumes as defined.  
- Starts services in dependency order, honoring `depends_on`.  
- Runs in **detached** mode (`-d`), so your shell prompt returns immediately.  
- Containers persist until you explicitly stop them (`docker compose stop` or `docker compose down`).  
  
---

## `docker compose run --build --rm financial-analyzer python3 main.py <TICKER>`

This is a **one-off** command: it builds the image if necessary, starts a container for the specified service, runs your custom command, then removes that container on exit.

  
- Targets only the `financial-analyzer` service—other services aren’t started automatically.  
- Overrides the default `command` in `docker-compose.yml` to run `python3 main.py <TICKER>`.  
- Builds the image first if there’s been a change to the `Dockerfile` or the context (`--build`).  
- Runs in the **foreground**, streaming logs to your terminal.  
- Cleans up the container when the process finishes (`--rm`), keeping your environment tidy.  
  
---

## Key Differences at a Glance

| Aspect                   | `up --build -d`                                     | `run --build --rm …`                                          |
|--------------------------|-----------------------------------------------------|---------------------------------------------------------------|
| Scope                    | All services                                        | Single service (`financial-analyzer`)                         |
| Image rebuild            | Yes, for every service                              | Yes, only for the targeted service                            |
| Startup order            | Honors service dependencies                         | Does not start linked/dependent services by default           |
| Command override         | Uses `command` from Compose file                    | Uses the command you supply (`python3 main.py <TICKER>`)      |
| Run mode                 | Detached (background)                               | Foreground                                                    |
| Container lifetime       | Persistent until manually stopped                   | Ephemeral (removed after exit)                                |
| Use case                 | Bring up entire application stack                   | Ad hoc or debugging runs of a single service                 |

---

## When to Use Which

- Use **`docker compose up --build -d`** when you want to launch or refresh your full application stack (e.g., web server, database, worker) and leave it running in the background.  
- Use **`docker compose run --build --rm …`** for quick, one-off executions such as data migrations, troubleshooting, or passing dynamic parameters (like different `<TICKER>` values) without polluting your list of containers.

---
# What Does `--rm` Mean?

The `--rm` flag tells Docker to automatically remove the container once its process exits.  

- Containers created with `run --rm` do not persist in the “docker ps -a” list.  
- Temporary filesystems, network attachments, and any state inside the container disappear on exit.  
- Keeps your environment clean by preventing accumulation of one-off containers.  

---

# `docker compose stop` vs `docker compose down`

| Aspect                | docker compose stop                          | docker compose down                                    |
|-----------------------|-----------------------------------------------|---------------------------------------------------------|
| What it does          | Stops running containers                     | Stops containers, removes containers, networks, volumes |
| Containers            | Remain on disk (stopped state)               | Removed entirely                                        |
| Networks              | Remain                                        | Removed                                                 |
| Volumes               | Remain                                        | Removed (unless you use `-v` to target only volumes)    |
| Use case              | Temporarily pause services                    | Teardown entire stack and free all resources            |

- `stop` is useful when you plan to restart the same containers quickly.  
- `down` is for a full teardown, cleaning up all artifacts so you can start completely fresh.  

---

# Re-Running `python3 main.py <TICKER>` in an Up-and-Running Stack

Once you’ve done `docker compose up --build -d`, your containers are already running in the background. To invoke `main.py` repeatedly without tearing down the whole stack, use the `exec` command:

```bash
docker compose exec financial-analyzer python3 main.py <TICKER>
```

- `exec` runs a new process inside the existing `financial-analyzer` container.  
- You don’t rebuild or recreate the container unless you change its image.  
- Logs stream to your terminal; hit Ctrl+C when you’re done.  

If you prefer a fresh container each time (with `--rm` cleanup), you can still use `run`:

```bash
docker compose run --rm financial-analyzer python3 main.py <TICKER>
```

This will spin up a disposable container for each execution, independent of the ones started by `up`.

---
# Difference between `docker exec` and `docker compose exec`

## Context of Each Command

Running a command _inside_ an existing container can be done either directly via Docker’s CLI or through Docker Compose. Both let you invoke a process in a live container, but they differ in syntax, defaults, and how they locate the target container.

---

## `docker exec -it financial-analyzer python3 src/main.py NVDA`

- Targets a container by its **name** or **ID** (here, `financial-analyzer`).  
- The `-i` flag keeps STDIN open; `-t` allocates a pseudo-TTY. Together they let you interactively run commands (e.g., for REPLs).  
- You must know the exact container name or look it up with `docker ps`.  
- You specify the full path to your script (`src/main.py`).  
- Does not know anything about your Compose project’s service names, networks, or working-directory defaults.

---

## `docker compose exec financial-analyzer python3 main.py <TICKER>`

- Targets a **service** defined in `docker-compose.yml` (here, `financial-analyzer`).  
- Automatically chooses the right container, even if Compose has added project prefixes or scaled the service.  
- Uses the working directory defined in the Compose file (`working_dir`), so you may not need `src/` in the path.  
- Runs in the context of your Compose network and shared volumes without extra flags.  
- By default, does **not** allocate a TTY or keep STDIN open. To make it interactive, add `-T` or `-d` flags as needed.

---

## Side-by-Side Comparison

| Aspect                        | `docker exec`                                            | `docker compose exec`                                     |
|-------------------------------|----------------------------------------------------------|-----------------------------------------------------------|
| Targeting                     | Container name or ID                                     | Compose service name                                      |
| Path resolution               | Absolute path inside container (e.g., `src/...`)         | Respects `working_dir` from Compose (no `src/` prefix)    |
| Networking                    | Uses Docker default networks                             | Joins Compose-defined networks                            |
| Interactive terminal defaults | `-it` required                                           | Non-interactive by default (add `-T` for silent, `-d` for detach) |
| Discovering container         | You must manually lookup name/ID                         | Compose handles lookup, even with multiple replicas       |
| Project isolation             | No awareness of Compose project context                  | Isolated per project name, avoids cross-stack conflicts   |

---

## Which One to Use?

- For **Compose-managed workflows**, prefer `docker compose exec`—it’s concise, picks the right container, and inherits your Compose settings.  
- For **ad hoc** interactions with any container (not just Compose), or when you already have a container’s ID, use `docker exec`.

---

## Extra Tips

- To run multiple commands in a row, you can wrap them in a shell:
  
  ```bash
  docker compose exec financial-analyzer sh -c "cd /app && python3 main.py AAPL && echo done"
  ```

- If you need an interactive Python REPL inside your app container:
  
  ```bash
  docker compose exec -it financial-analyzer python3
  ```

- Remember that `docker compose exec` won’t start a stopped container. If your service is down, first `docker compose up -d` it.
- 
