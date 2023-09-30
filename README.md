# Continuous deployment [text image retrieval service](https://github.com/duongngyn0510/text-image-retrieval) to [Google Kubernetes Engine](https://console.cloud.google.com/kubernetes/list/overview?project=striking-decker-399102) using CI/CD
## System Architecture
![](images/architecture.png)
# Table of Contents

1. [Create GKE Cluster](#1-create-gke-clusterCreate-GKE-Cluster)
2. [Deploy serving service manually](#2-deploy-serving-service-manually)

    1. [Deploy nginx ingress controller](#21-deploy-nginx-ingress-controller)

    2. [Deploy application](#22-deploy-application-to-gke-cluster-manually)

3. [Deploy monitoring service](#3-deploy-monitoring-service)

    1. [Deploy Prometheus service](#31-deploy-prometheus-service)

    2. [Deploy Grafana service](#32-deploy-grafana-service)


4. [Continuous deployment to GKE using Jenkins pipeline](#4-continuous-deployment-to-gke-using-jenkins-pipeline)

    1. [Create Google Compute Engine](#41-spin-up-your-instance)

    2. [Install Docker and Jenkins in GCE](#42-install-docker-and-jenkins)

    3. [Connect to Jenkins UI in GCE](#43-connect-to-jenkins-ui-in-compute-engine)

    4. [Setup Jenkins](#44-setup-jenkins)

    5. [Continuous deployment](#45-continuous-deployment)
## 1. Create GKE Cluster
### How-to Guide

#### 1.1. Create [Project](https://console.cloud.google.com/projectcreate) in GCP
#### 1.2. Install gcloud CLI
Gcloud CLI can be installed following this document https://cloud.google.com/sdk/docs/install#deb

Initialize the gcloud CLI
```bash
gcloud init
Y
```
+ A pop-up to select your Google account will appear, select the one you used to register GCP, and click the button Allow.

+ Go back to your terminal, in which you typed `gcloud init`, pick cloud project you using, and Enter.

+ Then type Y, type the ID number corresponding to **us-central1-f** (in my case), then Enter.

#### 1.3. Install gke-cloud-auth-plugin
```bash
sudo apt-get install google-cloud-cli-gke-gcloud-auth-plugin
```

#### 1.4. Create service account
Create your [service account](https://console.cloud.google.com/iam-admin/serviceaccounts), and select `Kubernetes Engine Admin` role (Full management of Kubernetes Clusters and their Kubernetes API objects) for your service account.

Create new key as json type for your service account. Download this json file and save it in `terraform` directory. Update `credentials` in `terraform/main.tf` with your json directory.

#### 1.5. Add permission for Project
Go to [IAM](https://console.cloud.google.com/iam-admin/iam), click on `GRANT ACCESS`, then add new principals, this principal is your service account created in step 1.3. Finally, select `Owner` role.
![](images/grant_access.png)

#### 1.6. Using [terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) to create GKE cluster.
Update your [project id](https://console.cloud.google.com/projectcreate) in `terraform/variables.tf`
Run the following commands to create GKE cluster:
```bash
gcloud auth application-default login
```

```bash
cd terraform
terraform init
terraform plan
terraform apply
```
+ GKE cluster is deployed at **us-central1-f** with its node machine type is: **n2-standard-2** (2 CPU, 8 GB RAM and costs 71$/1month).
+ Unable [Autopilot](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview) for the GKE cluster. When using Autopilot cluster, certain features of Standard GKE are not available, such as scraping node metrics from Prometheus service.

It can takes about 10 minutes for create successfully a GKE cluster. You can see that on [GKE UI](https://console.cloud.google.com/kubernetes/list)

![](images/gke_ui.png)
#### 1.7. Connect to the GKE cluster.
+ Go back to the [GKE UI](https://console.cloud.google.com/kubernetes/list).
+ Click on vertical ellipsis icon and select **Connect**.
You will see the popup Connect to the cluster as follows
![](images/connect_gke.png)
+ Copy the line `gcloud container clusters get-credentials ...` into your local terminal.

After run this command, the GKE cluster can be connected from local.
```bash
kubectx [YOUR_GKE_CLUSTER_ID]
```
## 2. Deploy serving service manually
Using [Helm chart](https://helm.sh/docs/topics/charts/) to deploy application on GKE cluster.

### How-to Guide

#### 2.1. Deploy nginx ingress controller
```bash
cd helm_charts/nginx_ingress
kubectl create ns nginx-ingress
kubens nginx-ingress
helm upgrade --install nginx-ingress-controller .
```
After that, nginx ingress controller will be created in `nginx-ingress` namespace.

#### 2.2. Deploy application to GKE cluster manually
Text-image retrieval service will be deployed with `NodePort` type (nginx ingress will route the request to this service) and 2 replica pods that maintain by `Deployment`.

Each pod contains the container running the [text-image retrieval application](https://github.com/duongngyn0510/text-image-retrieval).

The requests will initially arrive at the Nginx Ingress Gateway and will subsequently be routed to the service within the `model-serving` namespace of the GKE cluster.

```bash
cd helm_charts/app
kubectl create ns model-serving
kubens model-serving
helm upgrade --install app --set image.repository=duong05102002/text-image-retrieval-serving --set image.tag=v1.5 .
```

After that, application will be deployed successfully on GKE cluster. To test the api, you can do the following steps:

+ Obtain the IP address of nginx-ingress.
```bash
kubectl get ing
```

+ Add the domain name `retrieval.com` (set up in `helm_charts/app/templates/app_ingress.yaml`) of this IP to `/etc/hosts`
```bash
sudo nano /etc/hosts
[YOUR_INGRESS_IP_ADDRESS] retrieval.com
```
or you can utilize my Ingress IP address (valid until 27/11/2023 during the free trial period).
```bash
34.133.25.217 retrieval.com
```

+ Open web brower and type `retrieval.com/docs` to access the FastAPI UI and test the API.
    + For more intuitive responses, you can run `client.py` (Refresh the html page to display the images.)

        + Image query
            ```bash
            $ python client.py --save_dir temp.html --image_query your_image_file
            ```

            + **Top 8 products images similar with image query:**

                ![](app/images/woman_blazers.png)

                <html>
                    <body>
                        <div class="image-grid">
                <img src="https://storage.googleapis.com/fashion_image/168125.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/510624.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/919453.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/509864.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/1002845.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/6678.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/589519.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/67591.jpg" alt="Image" width="200" height="300">
                        </body>
                    </html>
        + Text query
            ```bash
            $ python client.py --save_dir temp.html --text_query your_text_query
            ```
            + **Top 8 products images similar with text query: crop top**
                <html>
                    <body>
                        <div class="image-grid">
                <img src="https://storage.googleapis.com/fashion_image/640366.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/965820.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/607634.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/673682.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/615135.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/38530.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/455345.jpg" alt="Image" width="200" height="300"><img src="https://storage.googleapis.com/fashion_image/742095.jpg" alt="Image" width="200" height="300">
                        </body>
                    </html>

## 3. Deploy monitoring service
I'm using Prometheus and Grafana for monitoring the health of both Node and pods that running application.

Prometheus will scrape metrics from both Node and pods in GKE cluster. Subsequently, Grafana will display information such as CPU and RAM usage for system health monitoring, and system health alerts will be sent to Discord.

### How-to Guide

#### 3.1. Deploy Prometheus service

+ Create Prometheus CRDs
```bash
cd helm_charts/prometheus-operator-crds
kubectl create ns monitoring
kubens monitoring
helm upgrade --install prometheus-crds .
```

+ Deploy Prometheus service (with `NodePort` type) to GKE cluster
```bash
cd helm_charts/prometheus
kubens monitoring
helm upgrade --install prometheus .
```

*Warnings about the health of the node and the pod running the application will be alerted to Discord. In this case, the alert will be triggered and sent to Discord when there is only 10% memory available in the node.*

Prometheus UI can be accessed by `[YOUR_NODEIP_ADDRESS]:30001`

**Note**:
+ Open [Firewall policies](https://console.cloud.google.com/net-security/firewall-manager/firewall-policies) to modify the protocols and ports corresponding to the node `Targets` in a GKE cluster. This will be accept incoming traffic on ports that you specific.
+ I'm using ephemeral IP addresses for the node, and these addresses will automatically change after a 24-hour period. You can change to static IP address for more stability or permanence.


#### 3.2. Deploy Grafana service
+ Deploy Grafana service (with `NodePort` type) to GKE cluster

```bash
cd helm_charts/grafana
kubens monitoring
helm upgrade --install grafana .
```

Grafana UI can be accessed by `[YOUR_NODEIP_ADDRESS]:30000` (with both user and password is `admin`)

Add Prometheus connector to Grafana with Prometheus server URL is: `[YOUR_NODEIP_ADDRESS]:30001`.

This is some `PromSQL` that you can use for monitoring the health of node and pod:
+ RAM usage of 2 pods that running application
```shell
container_memory_usage_bytes{container='app', namespace='model-serving'}
```
+ CPU usage of 2 pods that running application
```shell
rate(container_cpu_usage_seconds_total{container='app', namespace='model-serving'}[5m]) * 100
```

![](images/app_pod_metrics.png)

+ Node usage
![](images/node_metrics.png)

## 4. Continuous deployment to GKE using Jenkins pipeline

Jenkins is deployed on Google Compute Engine using [Ansible](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html) with a machine type is **n1-standard-2**.

### 4.1. Spin up your instance
Create your [service account](https://console.cloud.google.com/), and select [Compute Admin](https://cloud.google.com/compute/docs/access/iam#compute.admin) role (Full control of all Compute Engine resources) for your service account.

Create new key as json type for your service account. Download this json file and save it in `secret_keys` directory. Update your `project` and `service_account_file` in `ansible/deploy_jenkins/create_compute_instance.yaml`.

![](gifs/create_svc_acc_out.gif)

Go back to your terminal, please execute the following commands to create the Compute Engine instance:
```bash
cd ansible/deploy_jenkins
ansible-playbook create_compute_instance.yaml
```

![](gifs/create_compute_instance.gif)

Go to Settings, select [Metadata](https://console.cloud.google.com/compute/metadata) and add your SSH key.

Update the IP address of the newly created instance and the SSH key for connecting to the Compute Engine in the inventory file.

![](gifs/ssh_key_out.gif)
### 4.2. Install Docker and Jenkins in GCE

```bash
cd ansible/deploy_jenkins
ansible-playbook -i ../inventory deploy_jenkins.yaml
```

Wait a few minutes, if you see the output like this it indicates that Jenkins has been successfully installed on a Compute Engine instance.
![](images/install_jenkins_vm.png)
### 4.3. Connect to Jenkins UI in Compute Engine
Access the instance using the command:
```bash
ssh -i ~/.ssh/id_rsa YOUR_USERNAME@YOUR_EXTERNAL_IP
```
Check if jenkins container is already running ?
```bash
sudo docker ps
```

![](gifs/connect_vm_out.gif)
Open web brower and type `[YOUR_EXTERNAL_IP]:8081` for access Jenkins UI. To Unlock Jenkins, please execute the following commands:
```shell
sudo docker exec -ti jenkins bash
cat /var/jenkins_home/secrets/initialAdminPassword
```
Copy the password and you can access Jenkins UI.

It will take a few minutes for Jenkins to be set up successfully on their Compute Engine instance.

![](gifs/connect_jenkins_ui_out.gif)

Create your user ID, and Jenkins will be ready :D

### 4.4. Setup Jenkins
#### 4.4.1. Connect to Github repo
+ Add Jenkins url to webhooks in Github repo

![](gifs/add_webhook_out.gif)
+ Add Github credential to Jenkins (select appropriate scopes for the personal access token)


![](gifs/connect_github_out.gif)


#### 4.4.2. Add `PINECONE_APIKEY` for connecting to Pinecone Vector DB in the global environment varibles at `Manage Jenkins/System`


![](gifs/pinecone_apikey_out.gif)


#### 4.4.3. Add Dockerhub credential to Jenkins at `Manage Jenkins/Credentials`


![](gifs/dockerhub_out.gif)


#### 4.4.4. Install the Kubernetes, Docker, Docker Pineline, GCloud SDK Plugins at `Manage Jenkins/Plugins`

After successful installation, restart the Jenkins container in your Compute Engine instance:
```bash
sudo docker restart jenkins
```

![](gifs/install_plugin_out.gif)


#### 4.4.5. Set up a connection to GKE by adding the cluster certificate key at `Manage Jenkins/Clouds`.

Don't forget to grant permissions to the service account which is trying to connect to our cluster by the following command:

```shell
kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=system:anonymous

kubectl create clusterrolebinding cluster-admin-default-binding --clusterrole=cluster-admin --user=system:serviceaccount:model-serving:default
```

![](gifs/connect_gke_out.gif)

#### 4.4.6. Install Helm on Jenkins to enable application deployment to GKE cluster.

+ You can use the `Dockerfile-jenkins-k8s` to build a new Docker image. After that, push this newly created image to Dockerhub. Finally replace the image reference at `containerTemplate` in `Jenkinsfile` or you can reuse my image `duong05102002/jenkins-k8s:latest`


### 4.5. Continuous deployment
Create `model-serving` namespace first in your GKE cluster
```bash
kubectl create ns model-serving
```

The CI/CD pipeline will consist of three stages:
+ Tesing model correctness.
    + Replace the new pretrained model in `app/main.py`. I recommend accessing the pretrained model by downloading it from another storage, such as Google Drive or Hugging Face.
    + If you store the pretrained model directly in a directory and copy it to the Docker image during the application build, it may consume a significant amount of resource space (RAM) in the pod. This can result in pods not being started successfully.
+ Building the image, and pushing the image to Docker Hub.
+ Finally, it will deploy the application with the latest image from DockerHub to GKE cluster.

![](gifs/run_cicd_out.gif)


The pipeline will take about 8 minutes. You can confirm the successful deployment of the application to the GKE cluster if you see the following output in the pipeline log:
![](images/deploy_successfully_2gke.png)

Here is the Stage view in Jenkins pipeline:

![](images/pipeline.png)

Check whether the pods have been deployed successfully in the `models-serving` namespace.

![](gifs/get_pod_out.gif)

Test the API

![](gifs/test_api_out.gif)
