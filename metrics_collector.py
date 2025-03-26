from kubernetes import client, config
import re

# Load Kubernetes config
config.load_kube_config()

# Use CustomObjectsApi to get metrics
api = client.CustomObjectsApi()

namespace = "default"  # Change this if needed

def parse_cpu(cpu_str):
    """Convert CPU usage string (e.g., '1144557n') to millicores (mCPU)."""
    if cpu_str.endswith('n'):  # If in nanocores
        return int(cpu_str[:-1]) / 1_000_000  # Convert n to mCPU
    return int(cpu_str)  # Assume it's already in mCPU or cores

def parse_memory(mem_str):
    """Convert memory usage string (e.g., '176696Ki') to MiB."""
    match = re.match(r"(\d+)([a-zA-Z]+)?", mem_str)
    if match:
        value, unit = int(match.group(1)), match.group(2)
        if unit == "Ki":
            return value / 1024  # Convert KiB to MiB
        elif unit == "Mi":
            return value  # Already in MiB
        elif unit == "Gi":
            return value * 1024  # Convert GiB to MiB
    return int(mem_str)  # Default case (shouldn't happen)

def get_pod_metrics():
    """Fetch pod CPU and memory usage metrics from Kubernetes API."""
    try:
        # Fetch pod metrics
        metrics = api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods"
        )

        total_cpu = 0.0  # Sum of CPU in mCPU
        total_memory = 0.0  # Sum of memory in MiB
        cpu_memory_usage = []

        for item in metrics["items"]:
            pod_name = item["metadata"]["name"]
            cpu = parse_cpu(item["containers"][0]["usage"]["cpu"])
            memory = parse_memory(item["containers"][0]["usage"]["memory"])

            total_cpu += cpu
            total_memory += memory

            cpu_memory_usage.append({"pod": pod_name, "cpu": cpu, "memory": memory})

        return {
            "total_cpu_usage_mCPU": total_cpu,
            "total_memory_usage_MiB": total_memory,
            "pod_metrics": cpu_memory_usage
        }

    except Exception as e:
        print(f"Error fetching pod metrics: {e}")
        return None
