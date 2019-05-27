# nosql1h19-text-graph
![Logo](/docs/pictures/logo_text.png?raw=true)


[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=nosql1h19-text-graph&metric=ncloc)](https://sonarcloud.io/dashboard?id=nosql1h19-text-graph)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=nosql1h19-text-graph&metric=coverage)](https://sonarcloud.io/dashboard?id=nosql1h19-text-graph) 
![GitHub](https://img.shields.io/github/license/moevm/nosql1h19-text-graph.svg)
![GitHub top language](https://img.shields.io/github/languages/top/moevm/nosql1h19-text-graph.svg)
![GitHub repo size](https://img.shields.io/github/repo-size/moevm/nosql1h19-text-graph.svg)
![GitHub release](https://img.shields.io/github/release/moevm/nosql1h19-text-graph.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/moevm/nosql1h19-text-graph.svg)
![GitHub Release Date](https://img.shields.io/github/release-date/moevm/nosql1h19-text-graph.svg)

Программа для составления графа текста. Возможные варианты использования:
* Проверка группы работ на плагиат
* Поиск несвязанных фрагментов в художественном произведении/научной статье
# Установка
## Установка из исходников
См. [Запуск из исходников](https://github.com/moevm/nosql1h19-text-graph/wiki/Запуск-из-исходников)

## Установка в Docker
Нужна система с X Server.  
Если сокет X Server располагается в нестандартом месте, в 26-й строке docker-compose.yml нужно будет заменить /tmp/.X11-unix/ на используемый в системе путь до **папки** с сокетом X Server.  
Нужно, чтобы у Docker были права на работу с X Server, это можно сделать, например, так: `xhost +local:docker`.  
Если результат `echo $DISPLAY` не `:0`, подставьте ваше значение в 24-ю строчку docker-compose.yml  
Чтобы работал экспорт/импорт в БД, нужно скачать последние версии [apoc](https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases) и [graph algorithms](https://github.com/neo4j-contrib/neo4j-graph-algorithms/releases) в виде jar и положить их в папку neo4j_plugins.  
Запуск: `docker-compose up`. В окне логина заменить localhost на neo4j.

## Установка релиза
Для Bionic amd64 есть релиз в виде .deb. При установке таким образом [neo4j](https://neo4j.com/download/). [apoc](https://neo4j-contrib.github.io/neo4j-apoc-procedures/) и [graph algorithms](https://github.com/neo4j-contrib/neo4j-graph-algorithms) нужно поставить вручную. 

Также нужен [wkhtmltox](https://wkhtmltopdf.org/downloads.html).

# Скриншоты
![Screenshot 1](/docs/pictures/screenshot-1.png?raw=true)

![Screenshot 2](/docs/pictures/screenshot-2.png?raw=true)

![Screenshot 3](/docs/pictures/screenshot-3.png?raw=true)

![Screenshot 4](/docs/pictures/screenshot-4.png?raw=true)

# Авторы
Санкт-Петербургский Государственный Электротехнический университет "ЛЭТИ", кафедра МО ЭВМ

* Корытов Павел, 6304
* Пискунов Ярослав, 6304
* Цыганов Михаил, 6304
