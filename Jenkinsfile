pipeline {
    agent any

    options{
        // Max number of build logs to keep and days to keep
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        // Enable timestamp at each job in the pipeline
        timestamps()
    }

    // environment{
    //     registry = 'duong05102002/retrieval-local-service'
    //     registryCredential = 'dockerhub'
    // }

    stages {
        stage('Deploy') {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm' // Name of the container to be used for helm upgrade
                        image 'duong05102002/jenkins-k8s:latest' // The image containing helm
                        imagePullPolicy 'Always' // Always pull image in case of using the same tag
                    }
                }
            }
            steps {
                script {
                    container('helm') {
                        sh("helm upgrade --install app ./helm_charts/app --namespace model-serving")
                    }
                }
            }
        }
    }
}
