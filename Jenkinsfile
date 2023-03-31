#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}


node() {
    withEnv(["DOCKER_IMAGE_NAME=datapunt/gob_stuf:${env.BUILD_NUMBER}",
             "DOCKER_REGISTRY_HOST=https://docker-registry.secure.amsterdam.nl"
            ]) {

        stage("Checkout") {
            checkout scm
        }

        stage('Test') {
            lock("gob-stuf-test") {
		            tryStep "test", {
		                sh "docker-compose -p gob_stuf_service_${env.BRANCH_NAME} -f src/.jenkins/test/docker-compose.yml up --detach --force-recreate rabbitmq"
		                sh "docker-compose -p gob_stuf_service_${env.BRANCH_NAME} -f src/.jenkins/test/docker-compose.yml build --no-cache && " +
		                   "docker-compose -p gob_stuf_service_${env.BRANCH_NAME} -f src/.jenkins/test/docker-compose.yml run --rm test"
		                sh "docker-compose -p gob_stuf_service_${env.BRANCH_NAME} -f src/.jenkins/test/docker-compose.yml down"

		            }, {
		                sh "docker-compose -p gob_stuf_service_${env.BRANCH_NAME} -f src/.jenkins/test/docker-compose.yml down"
		            }
            }
        }

        stage("Build image") {
            tryStep "build", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker-registry') {
                    def image = docker.build("${DOCKER_IMAGE_NAME}",
                        "--no-cache " +
                        "--shm-size 1G " +
                        "--build-arg BUILD_ENV=acc " +
                        "--target application " +
                        " src")
                    image.push()
                }
            }
        }

        String BRANCH = "${env.BRANCH_NAME}"

        if (BRANCH == "develop") {

            stage('Push develop image') {
                tryStep "image tagging", {
                    docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker-registry') {
                       def image = docker.image("${DOCKER_IMAGE_NAME}")
                       image.pull()
                       image.push("develop")
                    }
                }
            }
        }

        if (BRANCH == "master") {

            stage('Push acceptance image') {
                tryStep "image tagging", {
                    docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker-registry') {
                        def image = docker.image("${DOCKER_IMAGE_NAME}")
                        image.pull()
                        image.push("acceptance")
                    }
                }
            }

            stage("Deploy to ACC") {
                tryStep "deployment", {
                    build job: 'Subtask_Openstack_Playbook',
                        parameters: [
                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy.yml'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_gob-stuf"]
                        ]
                }
            }
        }
    }
}
