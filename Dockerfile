# Use an official lightweight Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "app.py"]
