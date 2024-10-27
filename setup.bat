@echo off
echo Setting up Meme Generator project...

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements
pip install -r requirements.txt

echo Setup completed!