FROM python:3.11

ENV DEBIAN_FRONTEND=noninteractive

# Copy over the current dependencies and install them
RUN pip install crystal-toolkit ipykernel ipywidgets nglview plotly numpy dash pymatgen seaborn matplotlib pandas vtk ase gunicorn

# Copy over the rest of the files
COPY . .

# Install the current package as editable
RUN pip install -e .

ENV INPUT_FILE=./df.pkl

# Run the application
CMD gunicorn --bind 0.0.0.0:80 --workers=4 wsgi
