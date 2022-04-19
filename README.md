# Project Setup

1. Clone the project:

        $ git clone git_url
        $ cd dataengineeringbootcamp

## Local

2. Start airflow going to `airflow-local` directory

        $ cd airflow-local

4. Start docker-compose

        $ docker-compose -f docker-compose.yml up

4. Go to http://localhost:8080 and access airflow with the airflow user and password.


## GCP Cloud

### Requirements

- A [GCP account](https://console.cloud.google.com/) 
- A configured [gcloud SDK](https://cloud.google.com/sdk/docs/install-sdk)
- [Docker](https://www.docker.com/get-started/)
- [Kubectl](https://kubernetes.io/docs/reference/kubectl/kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)
- [KinD](https://kind.sigs.k8s.io/docs/user/quick-start/)

A gcloud project with the following APIs enabled:
- Kubernetes Engine API

#### Dependencies
- GCloud cli
- Kubernetes cluster version: 1.20 
- Terraform >= 1.0.11

### Running

#### Kubernetes

```shell
cd gcp
terraform init
terraform apply --var-file=terraform.tfvars
```
Once the cluster is created, set the kubectl context:

```
gcloud container clusters get-credentials $(terraform output -raw kubernetes_cluster_name) --region $(terraform output -raw location)
```

#### Airflow
To work with Airflow we will use a NFS service.

Create a namespace
```
kubectl create namespace nfs
```
Create the server 
```
kubectl -n nfs apply -f nfs-server.yaml 
```
Export the server
```
export NFS_SERVER=$(kubectl -n nfs get service/nfs-server -o jsonpath="{.spec.clusterIP}") 
```
Create a namespace for storage deployment:
```
kubectl create namespace storage
```
Add chart for the NFS-provisioner
```
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
```
Install NFS-external-provisioner
```
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
    --namespace storage \
    --set nfs.server=$NFS_SERVER \
    --set nfs.path=/
```

To deploy Airflow on Kuberntes, we need to create a namespace
```
kubectl create namespace airflow
kubectl get namespaces
```

Fetch the official Helm of Apache Airflow, then update the repo to make you got the latest version of it
```
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm search repo airflow
```
Deploy Airflow with Helm install
```
helm install airflow apache-airflow/airflow --namespace airflow --debug
```

Create a [service account in the project](https://console.cloud.google.com/iam-admin/serviceaccounts) and download the JSON file generated, save it under `credentials` folder.

To save the JSON key file as a Secret in GCP run
```
kubectl create secret generic terraform-user --from-file=credentials/key.json -n airflow
```

Create a Kubernetes [secret](https://kubernetes.io/docs/concepts/configuration/secret/) for connections
```
kubectl create secret generic airflow-connections --from-env-file=.env -n airflow
```

Check the secrets with
```
kubectl get secrets -n airflow
kubectl describe secrets/airflow-connections -n airflow
```

Create [ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/) for variables 
```
kubectl create configmap airflow-variables --from-env-file=.variables -n airflow
```

Check the variables with
```
kubectl describe configmaps airflow-variables -n airflow
kubectl get configmap airflow-variables -o yaml -n airflow
```

Install the airflow chart from the repository
```
helm install airflow -f airflow-cluster.yaml apache-airflow/airflow --namespace airflow
```
Verify that our pods are up and running
```
kubectl get pods -n airflow
```

##### Accessing to Airflow dashboard

The Helm chart shows how to connect:
```
You can now access your dashboard(s) by executing the following command(s) and visiting the corresponding port at localhost in your browser:

Airflow Webserver:     kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
Flower dashboard:      kubectl port-forward svc/airflow-flower 5555:5555 --namespace airflow
Default Webserver (Airflow UI) Login credentials:
    username: admin
    password: admin
Default Postgres connection credentials:
    username: postgres
    password: postgres
    port: 5432

You can get Fernet Key value by running the following:

    echo Fernet Key: $(kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode)
```


### Remove infrastructure
To destroy the GKE cluster run:

```
terraform destroy --var-file=terraform.tfvars
```

