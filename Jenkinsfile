pipeline {
    agent any

    stages {

        stage('Проверка Node.js') {
            steps {
                bat 'node --version'
                bat 'npm.cmd --version'
            }
        }

        stage('Установка зависимостей') {
            steps {
                bat 'python -m venv .venv'
                bat '.venv\\Scripts\\python.exe -m pip install --upgrade pip'
                bat '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Сборка Vue') {
            steps {
                bat 'cd client && npm.cmd install'
                bat 'cd client && npm.cmd run build'
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

        stage('Запуск приложения') {
            steps {     
                bat 'scripts\\start_backend.bat'
                bat 'scripts\\start_frontend.bat'
            }
        }
    }
}


// CI/CD test