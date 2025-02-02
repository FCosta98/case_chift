# Use an official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files into the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the `scripts/` folder into `/app/`
COPY . .

# Set the command to run the script
CMD ["python", "/app/script_odoo.py"]