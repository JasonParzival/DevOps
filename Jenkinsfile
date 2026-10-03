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

        stage('Очистка портов') {
            when {
                expression {
                    env.BRANCH == 'refs/heads/main'
                }
            }

            steps {
                powershell '''
                $ports = @(8000, 5173)

                foreach ($port in $ports) {
                    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue

                    foreach ($connection in $connections) {
                        Write-Host "Останавливаем PID $($connection.OwningProcess) на порту $port"
                        Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
                    }
                }
            '''
            }
        }

        stage('Запуск приложения') {
            when {
                expression {
                    env.BRANCH == 'refs/heads/main'
                }
            }

            steps { 
                bat 'scripts\\start_backend.bat'
                bat 'scripts\\start_frontend.bat'
                timeout(time: 10, unit: 'SECONDS') {
                    bat 'ping 127.0.0.1 -n 6 > nul'
                }
            }
        }

        stage('Проверка запущенных приложений') {
            when {
                expression {
                    env.BRANCH == 'refs/heads/main'
                }
            }

            steps {
                bat 'netstat -ano | findstr ":8000"'
                bat 'netstat -ano | findstr ":5173"'
            }
        }
    }
}


// dev