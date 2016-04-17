## Prerequisites
* Python 2.7

```
sudo apt-get install python2.7-dev
```

* Pip

```
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
```
## Initial Setup
* Install required Python Packages

```
sudo -H pip install -r requirements.txt
```

## Starting Development Server without automatic code reloading

```
python manage.py runserver 0.0.0.0:8000 --noreload
```

## Starting Scheduler (in leader server only)

```
celery -A executor worker -B
```