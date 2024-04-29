FROM python:3.10

ENV DEBIAN_FRONTEND=noninteractive

# Copy over the current dependencies and install them
RUN pip install pandas pymatgen dash crystal-toolkit dash-bootstrap-components gunicorn

# Copy over the rest of the files
COPY . .

# Install the current package as editable
RUN pip install --no-deps -e .

ENV INPUT_FILE=./df_small.pkl

# Run the application
CMD gunicorn --bind 0.0.0.0:$PORT --workers=4 wsgi
