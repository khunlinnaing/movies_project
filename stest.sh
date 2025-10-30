pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                script {
                    sh 'sshpass -p "Bl@kW" ssh -o StrictHostKeyChecking=no natasha@ststor01 "cd /var/www/html && git pull origin master" '
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    def response_code = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://stlb01:8091", returnStdout: true).trim()
                    sh 'sshpass -p "Bl@kW" ssh -o StrictHostKeyChecking=no natasha@ststor01 "cd /var/www/html && git pull origin master"'
                    if (response_code != '200'){
                        error('App not working after deployment. Http Codd ${response_code}')
                    }else{
                        echo "Deploy is success"
                    }
                }
            }
        }
    }
}
