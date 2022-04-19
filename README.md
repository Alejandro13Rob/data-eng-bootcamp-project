# Project Setup

1. Clone the project:

        $ git clone https://github.com/Alejandro13Rob/data-eng-bootcamp-project.git
        $ cd dataengineeringbootcamp

## Local
### Requirements

- [Docker](https://www.docker.com/get-started/)

2. Start airflow going to `airflow-local` directory

        $ cd airflow-local

4. Start docker-compose

        $ docker-compose -f docker-compose.yml up

4. Go to http://localhost:8080 and access airflow with the airflow user and password.


## Project in GCP

### Requirements

- A [GCP account](https://console.cloud.google.com/) 
- A configured [gcloud SDK](https://cloud.google.com/sdk/docs/install-sdk)
- [Docker](https://www.docker.com/get-started/)
- [Kubectl](https://kubernetes.io/docs/reference/kubectl/kubectl/)
- [Helm](https://helm.sh/docs/intro/install/)
- [KinD](https://kind.sigs.k8s.io/docs/user/quick-start/)
- A gcloud project with the following APIs enabled:
        - Kubernetes Engine API
- [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

### Running

#### Create a Kubernetes Cluster

```shell
cd terraform
terraform init
terraform apply
```

To work with Airflow we will use a NFS service. For that, make the bash script executable
```shell
chmod +x airflow_on_kubernetes.sh 
````

Run the bash script to create NFS server and run Airflow on the Kubernetes Cluster
```shell
. ./airflow_on_kubernetes.sh
```


***Problem solution:*** If you get a time out error, you could try with an old version of Airflow. Change it in the `.sh` file 
```shell
helm install airflow apache-airflow/airflow --namespace airflow --version 1.0.0
```

#### First time before running the project
You will need to create a new `values.yaml` according to the version of airflow you are running.
Follow the same commands as in `. ./airflow_on_kubernetes.sh` but before creating the secrets run

Generate a private key with ssh-keygen
````
ssh-keygen -t rsa
````
Create a [service account in the project](https://console.cloud.google.com/iam-admin/serviceaccounts) and download the JSON file generated, save it under `credentials` folder.

Follow the " create secrets" commands with your generated files and check them using
```
kubectl get secrets -n airflow
kubectl describe secrets/airflow-connections -n airflow
```

Deploy the public key on the Git repository (Settings -> Deploy Key)

Follow the Configmap commands and update your airflow installation.
Check the variables with
```
kubectl describe configmaps airflow-variables -n airflow
kubectl get configmap airflow-variables -o yaml -n airflow
```

##### Accessing to Airflow dashboard

Check your cluster is running with no problems
```
kubectl cluster-info
kubectl get nodes -o wide
```
Verify that our pods are up and running
```
kubectl get pods -n airflow
helm ls -n airflow
```

Access the webserver by running the following command in a new terminal
```
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
```
Visit 
```
http://localhost:8080/home
```
Also you can get Fernet Key value by running the following:
```
echo Fernet Key: $(kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode)
```


### Remove infrastructure
To destroy the GKE cluster run:

```
cd terraform
terraform destroy
```
