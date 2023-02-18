# TJTS5901 Course Template Project

This is the template for 2023 TJTS5901 Continuous Software Engineering -course.

- Sisu: <https://sisu.jyu.fi/student/courseunit/otm-38b7f26b-1cf9-4d2d-a29b-e1dcb5c87f00>
- Moodle: <https://moodle.jyu.fi/course/view.php?id=20888>


To get started with the project, see [`week_1.md`](./week_1.md)

## Start the app

Repository provides an `docker-compose` file to start the app. Edit `docker-compose.yml` to uncomment the ports, and run:

```sh
docker-compose up --build tjts5901
```

App can be also started from `Dockerfile`, with flask debug turned on, and current folder in editable mode. It has the benefit of automatically reflecting code changes in the app.

```sh
docker build -t tjts5901 .
docker run -it -p 5001:5001 -e "FLASK_DEBUG=1" -v "${PWD}:/app" tjts5901
```

Please see the `docs/tjts5901` folder for more complete documentation.

## To report a bug/security issue

Please, [fill our form](https://gitlab.jyu.fi/good-on-paper/good-paper-project/-/issues/new) to report any issues.

App:

https://goodonpaper-app.azurewebsites.net/
