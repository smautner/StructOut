rm dist -r
python setup.py sdist
twine upload dist/*
