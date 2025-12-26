# Use an official Python runtime as a parent image (matching user preference for 3.12)
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install basic system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
# Ensure Python outputs are sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1
# Ensure Gradio listens on all interfaces inside the container
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860

# Expose the default Gradio port
EXPOSE 7860

# Command to run the assistant
CMD ["python", "app.py"]
