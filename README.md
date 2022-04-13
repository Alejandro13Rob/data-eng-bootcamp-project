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

### Prerequisites

- A [GCP account](https://console.cloud.google.com/) 
- A configured gcloud SDK
- [Kubectl](https://kubernetes.io/docs/reference/kubectl/kubectl/)

A gcloud project with the following APIs enabled:
- Kubernetes Engine API

#### Dependencies
- gcloud cli
- Cluster version: 1.20 
- Terraform >= 1.0.11

### Installing

To have K8s cluster running:

Execute Terraform commands:

```
terraform init
```
```
terraform apply --var-file=terraform.tfvars
```
Once that the cluster is created, set the kubectl context:

```
gcloud container clusters get-credentials $(terraform output -raw kubernetes_cluster_name) --region $(terraform output -raw location)
```

To destroy the EKS cluster, we run:

```
terraform destroy --var-file=terraform.tfvars
```
### Airflow
To work with Airflow we will use a NFS service, we will created on the cluster.

Create a namespace for the nsf service
```
kubectl create namespace nfs
```
Now is time to create the nfs server 
```
kubectl -n nfs apply -f nfs/nfs-server.yaml 
```
export the nfs server.
```
export NFS_SERVER=$(kubectl -n nfs get service/nfs-server -o jsonpath="{.spec.clusterIP}") 
```

To install airflow go to the directory `kubernetes/`. [Install Airflow](../kubernetes/README.md)

