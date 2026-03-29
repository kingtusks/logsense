from tools.log_tools import (
    get_container_logs,
    get_all_container_logs,
    read_log_file,
    search_logs,
    journalctl,
    count_errors,
    get_failed_services,
    get_oom_events,
    get_failed_ssh_attempts,
)
from tools.ssh_tools import (
    docker_stats,
    ssh_disk_usage,
    ssh_memory,
    ssh_uptime,
)

all_tools = [
    get_container_logs,
    get_all_container_logs,
    read_log_file,
    search_logs,
    journalctl,
    count_errors,
    get_failed_services,
    get_oom_events,
    get_failed_ssh_attempts,
    docker_stats,
    ssh_disk_usage,
    ssh_memory,
    ssh_uptime,
]