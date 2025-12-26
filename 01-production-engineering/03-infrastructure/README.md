# Deep Dive: Infrastructure (Docker, Git & CI/CD)

**Context:** "It works on my machine" is the enemy of scale. In GenAI, environment consistency is critical (Python versions, CUDA drivers, C++ dependencies). This module ensures your code is portable, versioned, and automatically tested before it ever touches production.

## Module 1: Docker & Containerization (The Shipping Container)

**Goal:** Package your FastAPI/Python application into a lightweight, secure, and portable artifact that runs anywhere.

| Topic | Sub-Topic | One-Liner |
| :--- | :--- | :--- |
| **Dockerfile Optimization** | **Multi-Stage Builds** | Using a "Builder" stage to compile dependencies and a "Runner" stage to keep the final image tiny (removing gcc/build tools). |
| | **Layer Caching** | Ordering Dockerfile instructions (Copy requirements -> Install -> Copy Code) to speed up builds by 10x. |
| **Orchestration** | **Docker Compose** | Defining multi-container environments (FastAPI + Postgres + Redis) in a single YAML file for local dev. |
| | **Networking & DNS** | Understanding how containers talk to each other (e.g., `db_host="postgres"` instead of `localhost`). |
| **Security** | **Non-Root User** | Creating a specific user inside the container so the app doesn't have root privileges (Critical security best practice). |
| | **Environment Variables** | Injecting configuration at runtime (`docker run -e API_KEY=...`) rather than baking secrets into the image. |

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Hello Docker:** Write a `Dockerfile` that uses `python:3.10-slim`, copies a `main.py`, and runs it. Build and Run it.
2. **Port Mapping:** Expose a web server on port 8000 inside the container and map it to port 8080 on your host.
3. **Volume Mount:** Mount your local source code directory into the container so code changes reflect instantly (Hot Reload).
4. **Environment Check:** Run a container passing an ENV var. Have the python script print `os.getenv("MY_VAR")`.
5. **Clean Up:** Use `docker system prune` to clear out dangling images and stopped containers.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Slim Build" (Multi-Stage):**
   * *Task:* Create a Dockerfile for a FastAPI app with `pandas`. First build: Standard install (~500MB). Second build: Use Multi-stage to copy only installed packages (~150MB).
   * *Outcome:* Prove the size difference using `docker images`.

7. **The "Full Stack" (Compose):**
   * *Task:* Write a `docker-compose.yml` that spins up FastAPI and a Postgres DB. Configure FastAPI to connect to the DB using the service name `postgres`.
   * *Outcome:* The app successfully writes to the DB without you installing Postgres on your Mac/Windows.

8. **The "Layer Cache" Optimization:**
   * *Task:* Deliberately put `COPY . .` *before* `RUN pip install -r requirements.txt`. Change one line of code. Rebuild.
   * *Fix:* Swap the order. Change code. Rebuild. Notice the `pip install` step is "Cached" and instantaneous.

### 🏛️ Top-Tier Interview Questions
* "Explain the difference between `ENTRYPOINT` and `CMD` in a Dockerfile. When would you use one over the other?"
* "Why is `python:slim` preferred over `python:alpine` for Data Science/AI applications involving C-extensions (like NumPy/Pandas)?"
* "How do Docker Compose networks function? Why can't my container connect to `localhost` to reach a database running on my host machine?"

### ✅ Competency List
- [ ] Can reduce Docker image size by >40% using multi-stage builds.
- [ ] Can troubleshoot networking issues between two containers in the same Compose file.
- [ ] Can configure a "Hot Reload" development environment using Volumes.
- [ ] Can write a `.dockerignore` file to prevent copying `__pycache__` and `.env` into the image.

---

## Module 2: Git Flow & Version Control (The Safety Net)

**Goal:** Managing chaos. Moving from "final_final_v2.py" to a structured history where every change is documented, reversible, and reviewed.

| Topic | Sub-Topic | One-Liner |
| :--- | :--- | :--- |
| **Branching Strategy** | **Feature Branch Workflow** | Never committing to `main`. Creating short-lived branches (`feat/add-login`) and merging via Pull Request. |
| | **Semantic Versioning** | Tagging releases (v1.0.0, v1.1.0) based on Major (Break), Minor (Feature), Patch (Fix) logic. |
| **History Management** | **Interactive Rebase (`rebase -i`)** | Cleaning up messy commit history (squashing "fix typo" commits) before merging to shared branches. |
| | **Merge vs Rebase** | Understanding when to preserve history (Merge commit) vs linearize history (Rebase). |
| **Collaboration** | **Conventional Commits** | Using standard prefixes (`feat:`, `fix:`, `chore:`) to automate changelogs and versioning. |

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Branch & Switch:** Create a branch `dev`, make a change, switch back to `main`. Verify the change is gone.
2. **Staging:** Use `git add -p` to stage only *part* of a file (hunk) while leaving other changes unstaged.
3. **The Oops Fix:** Amend the previous commit message using `git commit --amend` because you made a typo.
4. **Tagging:** Create a lightweight tag `v1.0` and push it to remote.
5. **Git Log:** Use `git log --graph --oneline --all` to visualize the branch history in the terminal.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Clean History" (Squash):**
   * *Task:* Make 3 commits: "WIP", "Fixed typo", "Done".
   * *Practice:* Use `git rebase -i HEAD~3` to squash them into one clean commit: "feat: implement logic".

7. **The "Conflict Surgeon" (Merge Conflict):**
   * *Task:* Create two branches. Edit line 5 of `main.py` in both branches with *different* code. Commit both. Try to merge.
   * *Outcome:* Resolve the conflict manually in the editor and finalize the merge.

8. **The "Safe Undo" (Revert vs Reset):**
   * *Task:* Commit a "Bug".
   * *Practice:* Use `git revert <commit-hash>` to create a *new* commit that undoes the changes (Safe for shared branches), vs `git reset --hard` (Destructive/Local only).

### 🏛️ Top-Tier Interview Questions
* "Explain the difference between `git merge` and `git rebase`. Why is rebasing a shared branch considered dangerous?"
* "What is a 'Detached HEAD' state, and how do you recover your work if you commit while in it?"
* "How do Git Hooks (pre-commit) work, and how can they prevent bad code from entering the repo?"

### ✅ Competency List
- [ ] Can perform an interactive rebase to squash messy commits.
- [ ] Can resolve complex merge conflicts without losing code.
- [ ] Can use `git stash` to temporarily save work to switch branches.
- [ ] Can write commit messages following the Conventional Commits specification.

---

## Module 3: CI/CD Basics (The Assembly Line)

**Goal:** Automation. Ensuring that every time you push code, a robot checks your style, runs your tests, and tells you if you broke something.

| Topic | Sub-Topic | One-Liner |
| :--- | :--- | :--- |
| **GitHub Actions** | **Workflow Syntax (YAML)** | Defining triggers (`on: push`), jobs, and steps to execute commands in a VM. |
| | **Matrix Testing** | Automatically running your tests across multiple Python versions (3.9, 3.10, 3.11) in parallel. |
| **Quality Gates** | **Linting & Formatting** | Failing the pipeline if the code isn't formatted (Black/Ruff) or has type errors (MyPy). |
| | **Test Coverage** | Failing the pipeline if the test suite passes but covers less than 80% of the codebase. |
| **Secrets** | **Environment Secrets** | safely injecting API keys into the CI environment without exposing them in logs. |

### 🔬 Atomic Practice Labs (How to Practice)

**Part A: Foundation Drills (Syntax Muscle Memory)**
1. **Hello Action:** Create `.github/workflows/hello.yaml`. Make it print "Hello World" whenever you push to main.
2. **Linter Bot:** Add a step that installs `ruff` and runs `ruff check .`. Push bad code and watch it fail.
3. **Secret Echo:** Add a repository secret `MY_SECRET`. Try to print it in a step. Notice GitHub automatically masks it `***`.
4. **Artifacts:** Configure the workflow to upload a file (e.g., a log or coverage report) as an artifact you can download later.
5. **Manual Trigger:** Add `workflow_dispatch:` to the trigger list so you can run the action manually from the UI.

**Part B: Advanced Scenarios (Real-World Logic)**
6. **The "Gatekeeper" (Test Automation):**
   * *Task:* Create a workflow that runs `pytest`. Push a failing test.
   * *Outcome:* See the Red X on GitHub. Fix the test. Push again. See the Green Check.

7. **The "Matrix" (Multi-Version):**
   * *Task:* Configure a `strategy: matrix` to run your tests on Python 3.10 and 3.11 simultaneously.
   * *Outcome:* Two parallel jobs run in the Actions tab.

8. **The "Docker Publisher" (Build & Push):**
   * *Task:* Add a step that builds your Dockerfile and (optionally) pushes it to Docker Hub (or just builds it to verify syntax).

### 🏛️ Top-Tier Interview Questions
* "What is the difference between Continuous Integration (CI) and Continuous Deployment (CD)?"
* "How do you cache `pip` dependencies in GitHub Actions to speed up workflow execution time?"
* "Why should you never commit your `.env` file, and how do you handle those variables in a CI/CD pipeline?"

### ✅ Competency List
- [ ] Can write a GitHub Action that runs Linting, Type Checking, and Testing in parallel or sequence.
- [ ] Can configure a "Branch Protection Rule" that requires the CI to pass before merging.
- [ ] Can use Caching actions to reduce CI runtime.
- [ ] Can inspect CI logs to identify exactly which test failed and why.

---

## 🏆 Integrated Capstone Project: "The Ops Pipeline"

**Goal:** Combine Docker, Git, and CI/CD into a production-ready workflow.

**The Brief:**
Create a fully automated repository for a simple FastAPI app.

1.  **Local Dev (Docker Compose):**
    * Create a `docker-compose.yml` that runs FastAPI (with hot reload) and Redis.
    * Verify you can hit `localhost:8000` and it increments a counter in Redis.
2.  **Version Control (Git Flow):**
    * Create a branch `feat/counter`. Add the Redis logic.
    * Commit using conventional commits (`feat: add redis counter`).
3.  **The Guardian (CI Pipeline):**
    * Create a GitHub Action that triggers on Pull Requests.
    * Step 1: Check code formatting (Ruff).
    * Step 2: Spin up a Redis service container *inside* the CI.
    * Step 3: Run `pytest` (integration tests talking to that Redis).
4.  **The Delivery (Build):**
    * If the tests pass, run a final step that builds the production Docker image.

**Success Criteria:**
* You open a Pull Request with bad formatting -> CI Fails.
* You fix formatting -> CI Passes Lint -> Runs Tests.
* You merge to `main`.
* You can run `docker compose up` on a fresh machine and the app just works.