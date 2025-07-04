**Step 1: Start Services in the Background**
Run this command once to build and start the `financial-analyzer` and `redis` containers. The `-d` flag runs them in detached mode (in the background).

```bash
docker compose -f docker-compose-dev.yml up --build -d
```

**Step 2: Verify the Container is Running**
Check the status of your containers. You will now see that `financial-analyzer-2` is `Up`.

```bash
docker ps
```

**Step 3: Execute Interactive Commands**
Now you can use `docker exec` to run any command inside the running container.

*   **To run a financial analysis:**
    ```bash
    docker exec financial-analyzer-2 python3 main.py --ticker GOOGL
    ```

*   **To run your entire test suite:**
    ```bash
    docker exec financial-analyzer-2 pytest
    ```

*   **To open an interactive shell for debugging:**
    ```bash
    docker exec -it financial-analyzer-2 /bin/bash
    ```
    You can then run commands like `ls -l`, `cat src/financial_analysis/system.py`, or `python3` from inside the container. Type `exit` to leave the shell.

**Step 4: Stop Services When Finished**
When you are done with your development session, bring everything down cleanly.

```bash
docker compose -f docker-compose-dev.yml down
```

This updated configuration gives you a persistent development environment, making it much easier to run tests and perform ad-hoc analyses. The system is ready for your next command.

