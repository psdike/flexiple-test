import os
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
import subprocess
import yaml

def connect_to_cluster(kubeconfig_path=None):
    config.load_kube_config(kubeconfig_path)
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    return [node.metadata.name for node in nodes.items]

def install_helm_chart(release_name, chart_name, namespace, repo_url):
    subprocess.run(["helm", "repo", "add", chart_name, repo_url], check=True)
    subprocess.run(["helm", "repo", "update"], check=True)
    subprocess.run([
        "helm", "upgrade", "--install", release_name, chart_name + "/keda", 
        "--namespace", namespace, "--create-namespace"
    ], check=True)

def create_deployment(api_client, namespace, deployment_name, image, cpu_request, memory_request, cpu_limit, memory_limit, port):
    apps_v1 = client.AppsV1Api(api_client)
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": deployment_name, "namespace": namespace},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": deployment_name}},
            "template": {
                "metadata": {"labels": {"app": deployment_name}},
                "spec": {
                    "containers": [
                        {
                            "name": deployment_name,
                            "image": image,
                            "resources": {
                                "requests": {"cpu": cpu_request, "memory": memory_request},
                                "limits": {"cpu": cpu_limit, "memory": memory_limit},
                            },
                            "ports": [{"containerPort": port}],
                        }
                    ]
                },
            },
        },
    }

    try:
        return apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)
    except ApiException as e:
        if e.status == 409:  # Conflict
            print(f"Deployment '{deployment_name}' already exists. Updating it instead.")
            return apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        else:
            raise

def create_scaled_object(namespace, deployment_name, trigger_type, trigger_value):
    scaled_object_yaml = f"""
    apiVersion: keda.sh/v1alpha1
    kind: ScaledObject
    metadata:
      name: {deployment_name}-scaledobject
      namespace: {namespace}
    spec:
      scaleTargetRef:
        name: {deployment_name}
      minReplicaCount: 1
      maxReplicaCount: 10
      triggers:
        - type: {trigger_type}
          metadata:
            type: Utilization
            value: "{trigger_value}"
    """
    subprocess.run(["kubectl", "apply", "-f", "-"], input=scaled_object_yaml.encode(), check=True)

def get_deployment_status(api_client, namespace, deployment_name):
    apps_v1 = client.AppsV1Api(api_client)
    deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
    metrics = subprocess.run([
        "kubectl", "top", "pods", "-n", namespace, "--selector=app=" + deployment_name
    ], capture_output=True, text=True)
    return {
        "deployment_status": deployment.status.conditions,
        "resource_metrics": metrics.stdout,
    }

def main():
    kubeconfig_path = os.getenv("KUBECONFIG", "~/.kube/config")
    namespace = "keda"
    deployment_name = "flexiple-deployment"
    image = "nginx:latest"
    cpu_request, memory_request = "250m", "256Mi"
    cpu_limit, memory_limit = "500m", "512Mi"
    port = 80

    connect_to_cluster(kubeconfig_path)
    install_helm_chart("kedacore", "keda", namespace, "https://kedacore.github.io/charts")
    api_client = client.ApiClient()
    config.load_kube_config()

    api_client = client.ApiClient()
    namespace = "default"
    deployment_name = "flexiple-deployment"
    image = "nginx:latest"
    cpu_request = "250m"
    memory_request = "128Mi"
    cpu_limit = "500m"
    memory_limit = "256Mi"
    port = 80

    create_deployment(api_client, namespace, deployment_name, image, cpu_request, memory_request, cpu_limit, memory_limit, port)
    create_scaled_object(namespace, deployment_name, "cpu", 50)
    status = get_deployment_status(api_client, namespace, deployment_name)
    print(status)

if __name__ == "__main__":
    main()
