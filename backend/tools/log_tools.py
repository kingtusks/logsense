import docker
from langchain_core.tools import tool
from tools.ssh_tools import _ssh


@tool
def get_container_logs(name: str, lines: int = 100, since: str = "") -> str:
    """
    Gets logs from a Docker container.
    name: container name
    lines: number of lines to fetch (default 100)
    since: optional time filter e.g. '1h', '30m', '2024-01-01T00:00:00'
    """
    try:
        client = docker.from_env()
        kwargs = {"tail": lines, "timestamps": True}
        if since:
            kwargs["since"] = since
        logs = client.containers.get(name).logs(**kwargs).decode()
        return logs or "no logs"
    except Exception as e:
        return f"error: {e}"


@tool
def get_all_container_logs(lines: int = 50) -> str:
    """Fetches the last N lines of logs from every running Docker container"""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        if not containers:
            return "no running containers"
        output = []
        for c in containers:
            logs = c.logs(tail=lines, timestamps=True).decode().strip()
            output.append(f"=== {c.name} ===\n{logs or 'no logs'}")
        return "\n\n".join(output)
    except Exception as e:
        return f"error: {e}"


@tool
def read_log_file(path: str, lines: int = 100) -> str:
    """
    Reads a log file on the remote server.
    path: full path e.g. /var/log/syslog, /var/log/nginx/error.log
    lines: number of lines from the end (default 100)
    """
    return _ssh(f"tail -n {lines} {path}")


@tool
def search_logs(path: str, pattern: str, lines: int = 200) -> str:
    """
    Searches a log file for a pattern using grep.
    path: full path to log file
    pattern: search string or regex
    lines: how many lines of the file to search from the end (default 200)
    """
    return _ssh(f"tail -n {lines} {path} | grep -i '{pattern}' || echo 'no matches found'")


@tool
def journalctl(service: str = "", lines: int = 100, since: str = "") -> str:
    """
    Reads systemd journal logs.
    service: optional service name e.g. nginx, docker, ssh (leave empty for system-wide)
    lines: number of lines (default 100)
    since: optional time filter e.g. '1 hour ago', 'today', '2024-01-01 00:00:00'
    """
    cmd = "journalctl"
    if service:
        cmd += f" -u {service}"
    if since:
        cmd += f" --since '{since}'"
    cmd += f" -n {lines} --no-pager"
    return _ssh(cmd)


@tool
def count_errors(path: str, since_minutes: int = 60) -> str:
    """
    Counts error/warn/critical occurrences in a log file over the last N minutes.
    path: full path to log file
    since_minutes: how many minutes back to look (default 60)
    """
    return _ssh(
        f"tail -n 5000 {path} | grep -ciE '(error|warn|crit|fatal|exception|traceback)' || echo 0"
    )


@tool
def get_failed_services() -> str:
    """Lists all failed systemd services on the remote server"""
    return _ssh("systemctl --failed --no-pager")


@tool
def get_oom_events() -> str:
    """Checks for OOM (out of memory) kill events in dmesg and syslog"""
    dmesg = _ssh("dmesg --ctime | grep -i 'oom\\|killed process\\|out of memory' | tail -20 || echo 'none found'")
    syslog = _ssh("grep -i 'oom\\|killed process\\|out of memory' /var/log/syslog 2>/dev/null | tail -20 || echo 'none found'")
    return f"=== dmesg ===\n{dmesg}\n\n=== syslog ===\n{syslog}"


@tool
def get_failed_ssh_attempts(since_minutes: int = 60) -> str:
    """
    Shows failed SSH login attempts from auth.log.
    since_minutes: how far back to look (default 60)
    """
    return _ssh(
        "grep 'Failed password\\|Invalid user\\|authentication failure' /var/log/auth.log 2>/dev/null "
        "| tail -50 || echo 'no failed attempts found or auth.log not accessible'"
    )