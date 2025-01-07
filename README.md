# Projet_APP_Recherche

## Setting up the Virtual Environment

Follow these steps to set up and use the virtual environment for this project.

### 1. Clone the repository

Start by cloning the repository to your local machine:

```bash
git clone git@github.com:ghostondancefloor/Projet_APP_Recherche.git
```

If Python is not installed, you can download it from the official Python website: https://www.python.org/downloads/

### 2. Create a Virtual Environment
Navigate to the root directory of your project and run the following command to create a virtual environment:

```bash
python -m venv venv
```
This will create a directory named venv in your project folder, which will contain a clean Python environment.

### 3. Activate the Virtual Environment
Windows:
```bash
.\venv\Scripts\activate

MacOS/Linux:
```bash
source venv/bin/activate
```
You should see the virtual environment name (venv) in your terminal prompt, indicating that the virtual environment is active.

### 4. Install Dependencies
Once the virtual environment is activated, you can install the project dependencies. With the requirements.txt file, you can install all dependencies by running:

```bash
pip install -r requirements.txt
```

### 5. Deactivate the Virtual Environment
When you're done working on the project, you can deactivate the virtual environment by running:

```bash
deactivate
```
This will return you to your global Python environment.

6. (Optional) Managing Dependencies
To freeze the current state of your virtual environment's installed packages into a requirements.txt file, run:

```bash
pip freeze > requirements.txt
```
This will allow others to install the exact same dependencies by running pip install -r requirements.txt