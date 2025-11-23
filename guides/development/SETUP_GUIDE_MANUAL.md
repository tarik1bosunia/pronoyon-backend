## install python is python3 for ubuntu
```bash
sudo apt update
sudo apt install python-is-python3
```

## initial setup
```bash
python -m venv venv
source venv/bin/activate
```

## create `requirements.txt` add `Django` on it then
(also keep in mind when any pacakge need to install just add it in the `requirements.txt` file then run the following command)

```bash
pip install -r requirements.txt
```

## create django project

```bash
django-admin startproject config .
```

## project structure now
```
replycompass/                        # ✅ Project root (where you are now)
├── manage.py                        # ✅ Correct location
├── config/                          # ✅ Configuration package
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── venv/                           # ✅ Your existing files preserved
```

## Split config/settings.py like this:
```
config/
└── settings/
    ├── __init__.py
    ├── base.py
    ├── local.py
    ├── docker.py
    └── production.py
```


## create .gitignore
