from flask import Flask, jsonify
from metrics_collector import get_pod_metrics

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_metrics():
    metrics_result = get_pod_metrics()
    if metrics_result:
        # Filter out only the total parameters
        total_metrics = {
            "total_cpu_usage_mCPU": metrics_result['total_cpu_usage_mCPU'],
            "total_memory_usage_MiB": metrics_result['total_memory_usage_MiB']
        }
        return jsonify(total_metrics)
    else:
        return jsonify({"error": "Failed to fetch metrics"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)