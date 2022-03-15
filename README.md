# Reader-Translator-Generator (RTG)  (Streamlit Version)

### Что может делать данное приложение?

Перевод с любого языка мира (более 500) на английский.

### Как установить? 

Открыть командную строку и ввести следующий код: 
```
git clone https://github.com/Lev-etd/rtg_streamlit.git
cd rtg_streamlit/
bash setup.sh
streamlit run app_streamlit.py --server.address 0.0.0.0 --server.port 8080
```
### Системные требования
Оперативная память: 7 гб  
Память на жёстком диске: 2 гб

При первом запуске будет скачан файл на 1.5 гб, поэтому первый запуск приложения будет происходить дотаточно долго.

#### Для пользователей Windows. 
##### Для установки WSL (программы для выполнения Linux команд на Windows) 

Пройдите в Настройки > Обновление и безопасность > Для Разработчиков. Отметьте галочкой "Режим разработчика". Найдите “Windows Features”, выберите “Включить/Выключить Windows features”.
В списке найдите WSL, отметьте галочкой, и установите его. После установки перезагрузите ПК. Откройте Command Prompt или PowerShell и введите команлы выше.

#### Для пользователей Mac. 

Открыть командную строку и ввести следующий код: 
```
git clone https://github.com/Lev-etd/rtg_streamlit.git
cd rtg_streamlit/
bash setup_mac.sh
streamlit run app_streamlit.py --server.address 0.0.0.0 --server.port 8080
```
