# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install any needed packages specified in requirements.txt
COPY pyproject.toml /app
RUN uv pip install --system --no-cache .

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 8888 available to the world outside this container
EXPOSE 8888

# Run main.py when the container launches
CMD ["uv","run","main.py"]
