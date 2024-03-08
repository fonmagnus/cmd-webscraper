# CMD Webscraper

This is a mini-project to implement a webscraper using a shell command line. The purpose of this project is to : 

- Scrap a web pages given the URL (can be multiple) of pages by a command line

## How to Run it

### Prerequisites

If you want to run this application using docker, please make sure you have installed Docker in your local machine

If you want to run this application using local machine, please have a `python3.8` and `sqlite3` driver installed in your local machine

### Instructions

#### Read this section if you're using docker for running the app

1. Build the docker

```docker build -t cmd-webscraper .```

2. Run the docker

```docker run -it cmd-webscraper bash```

#### This is the main section of the app

1. Whether you running this app with or without the Docker Instance, you can run the scraper by using this command : 

```./fetch <url_1> <url_2> ... <url_N>```
where `<url_i>` is the $i$-th URL of the web page you want to scrap from


2. You can also fetch and download the assets by adding arguments `--with-assets` at the end of the arguments. This flag args will indicate that we want to download images / assets from the respective website

3. You can also give arguments of `--metadata` followed by the URL like this

```./fetch --metadata <url>```

To see the fetched metadata of the web pages including : images, links, and last updated

### Expected Results

- The scraped web-pages will be saved inside a directory named `scraped_pages/<url>` where `<url>` will be the directory name with the requested URL consists of the main HTML and the assets of the pages

- The metadata of images and links scraped from the website will be saved under the `scraped_pages/metadata.db`. The DB by default is using `sqlite` driver

### Utility Classes

The `utils` directory is used to store some classes that act as a utility to help us performing the task. The classes consists of : 

- `CmdParser` : is used to parse the command line arguments
- `Scraper` : is used to perform the webscraping. I use `bs4` (a.k.a. Beautiful Soup library) to perform the scrap
- `Repository` : is used to store the metadata of the web page (such as images, links, etc) inside the Database (sqlite3)

### How it Works 

1. First the `CmdParser` will parse the arguments and will pass the given arguments
2. Then the `Scraper` will look into the URL. For the case of multiple URLs, the scraper will run the scraping process concurrently and wait until all the scraping process completed. This concurrency is implemented using python `threading` library
3. For each scraping process, the scraper will fetch the following information to the database: the site title, images, and links attributes. this will be used for fetching the metadata later on
4. At the end of each scraping process, the scraped page will have the URL as its name and will be stored under the `scraped_pages` directory along with its HTML file (and assets if the `--with-assets` flag argument is given)

### Known Issues

Although the scraper for the assets successfully saving some of the assets, however for some pages, the assets are not loaded when we open the static HTML page. The possible suspicion as a root cause for this issue is how the asset directory path is stored

### Demo

- Performing default scrap

![](https://i.ibb.co/2gthN87/ezgif-5-a27454a5f1.gif)

- Performing scrap with assets

![](https://i.ibb.co/mRTsY59/ezgif-5-5d7774603c.gif)