import paramiko
from decouple import config
from langchain_core.tools import tool


def _ssh(command: str) -> str:
    host = config("SSH_HOST", default=None)
    user = config("SSH_USER", default=None)
    password = config("SSH_PASSWORD", default=None)

    if not host or not user:
        return "SSH not configured — set SSH_HOST and SSH_USER in .env"
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password)
        _, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        client.close()
        return output or error or "command ran with no output"
    except Exception as e:
        return f"error: {e}"


@tool
def docker_stats() -> str:
    """Shows CPU and memory usage for all running containers"""
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list()
        if not containers:
            return "no running containers"
        lines = []
        for c in containers:
            stats = c.stats(stream=False)
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            num_cpus = stats["cpu_stats"].get("online_cpus", 1)
            cpu_pct = round((cpu_delta / system_delta) * num_cpus * 100, 2) if system_delta > 0 else 0.0
            mem_usage = round(stats["memory_stats"]["usage"] / 1_000_000, 1)
            mem_limit = round(stats["memory_stats"]["limit"] / 1_000_000, 1)
            lines.append(f"{c.name}: CPU {cpu_pct}% | MEM {mem_usage}MB / {mem_limit}MB")
        return "\n".join(lines)
    except Exception as e:
        return f"error: {e}"


@tool
def ssh_disk_usage() -> str:
    """Shows disk usage on the remote server"""
    return _ssh("df -h")


@tool
def ssh_memory() -> str:
    """Shows memory usage on the remote server"""
    return _ssh("free -h")


@tool
def ssh_uptime() -> str:
    """Shows how long the remote server has been running"""
    return _ssh("uptime")