![alt text](./screenshots/step0.png)
![alt text](./screenshots/step1.png)
Докер не нашёл образ локально. Скачал образ из DockerHub. Создал и запустил контейнер из скачанного образа. Контейнер вывел приветственное сообщение и завершился
![alt text](./screenshots/step2.png)
![alt text](./screenshots/step3.png)
Контейнер demo запущен в фоне, порт 80 контейнера проброшен на 8080 хоста. При открытии http://localhost:8080 виден ответ сервера с hostname и IP. docker ps показал только работающие контейнеры (demo). docker ps -a показал все контейнеры, включая остановленные (hello-world).
![alt text](./screenshots/step4.png)
Вывелись логи — запуск сервиса и HTTP-запросы из браузера.
![alt text](./screenshots/step5.png)
Узнали hostname контейнера и его IP.
![alt text](./screenshots/step6.png)
Показано использование CPU и памяти контейнером demo.
![alt text](./screenshots/step7.png)
Полная информация о контейнере demo (всё в один скриншот не поместилось)
![alt text](./screenshots/step8.png)
Контейнер остановился (статус Exited), затем запустился снова — все данные сохранились.
![alt text](./screenshots/step9.png)
Остановка и удаление контейнера demo
![alt text](./screenshots/step10.png)
Посмотрели локальные образы, затем удалили их.
![alt text](./screenshots/step11.png)
system df показал занимаемое место; prune удалил неиспользуемые контейнеры, сети, кэш; -a удалил также неиспользуемые образы.

Для второй части я выбрал Eatherpad. Выбирал наугад
![alt text](./screenshots/step12.png)
docker run -d --name pad -p 9001:9001 etherpad/etherpad
-d — запуск в фоне
--name pad — имя контейнера
-p 9001:9001 — проброс порта (порт контейнера 9001 на порт хоста 9001)
etherpad/etherpad — официальный образ
![alt text](./screenshots/step13.png)
![alt text](./screenshots/step14.png)
Основной процесс - это node
![alt text](./screenshots/step15.png)
![alt text](./screenshots/step16.png)