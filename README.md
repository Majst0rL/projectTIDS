RabbitMQ-Integrated Book Management Application
===============================================

This project demonstrates a Flask-based application that integrates multiple technologies. It uses JSON for data storage and transfer, REST for communication, API usage, open data in the form of PCAXIS files, web scraping, and RabbitMQ for message brokering. The application includes various pages, each showcasing a different type of technology in action.

Prerequisites
-------------

Before starting the application, ensure you have the following installed:

* **Python 3.10 or newer**: Install Python from [python.org](https://www.python.org/).
* **Docker**: Install Docker from [docker.com](https://www.docker.com/).
* **RabbitMQ Docker Image**: Ensure Docker can run the RabbitMQ container.
* Flask, requests, redis, pandas, pyaxis, selenium, pika, services.
* Browser driver (Edge,chrome, opera, etc...)
    

Setup Instructions
------------------

### 1\. Start RabbitMQ Using Docker

Start the RabbitMQ server by running the following command:

`docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management`

* **5672**: Port for RabbitMQ messaging.
* **15672**: Port for RabbitMQ web management interface (accessible at [http://localhost:15672](http://localhost:15672)).


### 2\. Run the Application

Start the Flask application by running the following commands:

`python main.py`

The application will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### 3\. Start the Consumer Script

Run the RabbitMQ consumer script to handle events:

`python consume_script.py`

Features
--------

* **Home Page**: Displays top books from the Open Library API.
* **Search**: Search for books using the Google Books API.
* **Top 100 Slovenia**: View top books scraped from the COBISS website.
* **My List**: Add, update, and delete books in your personal list.
* **OpenData**: Shows graph from PCAXIS file
* **RabbitMQ**: Demonstrates publishing and consuming messages via RabbitMQ.
    

Folder Structure
----------------

* app/ 
  * services/: Contains scripts for data fetching, RabbitMQ event handling, and scraping. 
  * routes.py & rabbitmq_routes.py: Defines routes for the web application.
* templates/: Contains HTML templates for the application. 
* static/: Contains static assets such as CSS files. 
* main.py: Entry point for running the Flask application. 
* consume_script.py: Script for consuming RabbitMQ messages.
    

Troubleshooting
---------------
* Ensure that you have installed all the required packages from `requirements.txt`.
* Ensure that you added your browser driver path to scraper.py
* Ensure that you have the `H092S.PX` file in the root directory.
* Ensure Docker is running and the RabbitMQ container is started. 
* Verify that ports 5672 and 15672 are not blocked by your firewall. 
* Check the RabbitMQ management interface for queue and message status at [http://localhost:15672](http://localhost:15672).