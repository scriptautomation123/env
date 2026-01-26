# Development Container Configuration

This directory contains the configuration for a Development Container (devcontainer) that provides a complete Java development environment with Docker support.

## Features

### Core Development Tools
- **Java 21 (Eclipse Temurin)**: Latest LTS version, automatically updated
- **Maven**: Latest version, automatically updated via SDKMAN
- **Docker & Docker Compose**: Full Docker-in-Docker support for container operations

### VS Code Extensions

The devcontainer comes pre-configured with the following extensions:

#### Version Control & Collaboration
- GitLens - Enhanced Git capabilities
- Add to .gitignore - Easy gitignore management

#### Code Quality & Analysis
- SonarLint - Code quality and security analysis

#### UI & Themes
- Peacock - Color your workspace
- Night Owl - Theme
- Eva Theme - Theme collection
- Andromeda - Theme
- Nicer High Contrast - Theme
- Material Icon Theme - File icons

#### Productivity
- Code Runner - Run code snippets quickly
- Rainbow CSV - CSV file visualization
- Markdown Preview Enhanced - Better markdown support

#### Container & Database
- Docker - Container management (ms-azuretools.vscode-containers)
- Oracle SQL Developer - Database management

#### AI & Context
- Context7 MCP - Upstash context management

## Usage

### Opening in VS Code

1. **Prerequisites**:
   - Install [Visual Studio Code](https://code.visualstudio.com/)
   - Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - Ensure Docker is running on your system

2. **Open the project**:
   - Open this repository in VS Code
   - Click the notification to "Reopen in Container" or
   - Press `F1` and select "Dev Containers: Reopen in Container"

3. **First-time setup**:
   - The container will build automatically (this may take a few minutes)
   - All extensions will be installed automatically
   - Java, Maven, Docker, and Docker Compose will be verified via the post-create command

### Verifying the Setup

After the container starts, you can verify the installations:

```bash
# Check Java version (should be Java 21)
java -version

# Check Maven version
mvn -version

# Check Docker version
docker --version

# Check Docker Compose version
docker compose version
```

## Docker-in-Docker Support

This devcontainer includes Docker-in-Docker (DinD) support, which means you can:
- Build Docker images inside the container
- Run docker-compose commands
- Create and manage containers and networks
- Use all Docker CLI features

The Docker socket is mounted from the host, allowing seamless integration with the host Docker daemon.

## Customization

To customize this devcontainer:

1. **Add more extensions**: Edit the `extensions` array in `devcontainer.json`
2. **Modify Java/Maven versions**: Update the `features` section
3. **Add custom tools**: Use `postCreateCommand` for additional setup
4. **Adjust settings**: Modify the `settings` object in `customizations.vscode`

## Benefits

- ✅ **Consistent Environment**: All team members use the same development setup
- ✅ **Quick Onboarding**: New developers can start coding in minutes
- ✅ **Isolated Dependencies**: No conflicts with local machine installations
- ✅ **Docker Support**: Full container development capabilities
- ✅ **Pre-configured Extensions**: All necessary tools ready to use
- ✅ **Latest Versions**: Java and Maven automatically use the latest stable versions

## Troubleshooting

### Container fails to build
- Ensure Docker is running and has sufficient resources
- Check Docker Desktop settings (at least 4GB RAM recommended)

### Docker commands not working inside container
- Verify Docker-in-Docker feature is enabled
- Check if the Docker socket mount is working: `ls -la /var/run/docker.sock`

### Extensions not loading
- Rebuild the container: `Dev Containers: Rebuild Container`
- Check the VS Code output panel for extension installation logs

## Learn More

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Features](https://containers.dev/features)
- [Java Development in Containers](https://code.visualstudio.com/docs/java/java-container)
