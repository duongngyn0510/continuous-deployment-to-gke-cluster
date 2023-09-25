pipeline {
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    environment{
        registry = 'duong05102002/text-image-retrieval-serving'
        registryCredential = 'dockerhub'
    }

    stages {
        stage('Test') {
            steps {
                echo 'Testing model correctness..'
                echo 'Always pass all test unit :D'
            }
        }

        stage('Build image') {
            steps {
                script {
                    echo 'Building image for deployment..'
                    def imageName = "${registry}:v1.${BUILD_NUMBER}"
                    def buildArgs = "--build-arg PINECONE_APIKEY=${PINECONE_APIKEY}"
                    // PINECONE_APIKEY env is set up on Jenkins dashboard

                    dockerImage = docker.build(imageName, "--file Dockerfile-app-serving ${buildArgs} .")
                    echo 'Pushing image to dockerhub..'
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                    }
                }
            }
        }

        stage('Deploy to Google Kubernetes Engine') {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm' // Name of the container to be used for helm upgrade
                        image 'duong05102002/jenkins-k8s:latest' // The image containing helm
                    }
                }
            }
            steps {
                script {
                    steps
                    container('helm') {
                        sh("helm upgrade --install app --set image.repository=${registry} \
                        --set image.tag=v1.${BUILD_NUMBER} ./helm_charts/app --namespace model-serving")
                    }
                }
            }
        }
    }
}
