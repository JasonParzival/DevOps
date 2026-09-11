pipeline {
    agent any

    stages {

        stage('Установка зависимостей') {
            steps {
                bat 'python -m venv .venv'
                bat '.venv\\Scripts\\python.exe -m pip install --upgrade pip'
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Миграции базы данных') {
            steps {
                bat '.venv\\Scripts\\python.exe manage.py migrate --noinput'
            }
        }

        stage('Запуск тестов') {
            steps {
                bat '.venv\\Scripts\\python.exe -m pytest'
            }
        }
    }
}