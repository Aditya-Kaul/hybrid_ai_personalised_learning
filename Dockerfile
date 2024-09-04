# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pysqlite3-binary to address SQLite version issues
RUN pip install --no-cache-dir pysqlite3-binary==0.5.1

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Create and set environment variables
ENV GOOGLE_API_KEY="AIzaSyDjs6-jQNsmYFcqK54Mk5zsPDIBwJlk29E"

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]