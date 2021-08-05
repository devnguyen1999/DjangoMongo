# Use an official Python runtime as a parent image
FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /home/DjangoMongo
WORKDIR /home/DjangoMongo
RUN apt-get update && apt-get upgrade -y
COPY ./ ./
RUN pip install -r requirements.txt
# Django service
EXPOSE 8000

# Be sure to use 0.0.0.0 for the host within the Docker container,
# otherwise the browser won't be able to find it
CMD python manage.py runserver 0.0.0.0:8000