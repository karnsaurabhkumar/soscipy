#python setup.py sdist bdist_wheel
python3 -m pip install --upgrade build
#pip list --format=freeze > requirements.txt
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload --repository testpypi dist/*
python3 -m twine upload --repository pypi dist/*
