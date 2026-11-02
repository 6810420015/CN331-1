# CN331 Debate Platform

A Thai-language debate platform built with Django. Members can create a topic, define the sides people can vote for, set an optional closing time, and explain their vote in a comment. Topic pages show the discussion and a live vote breakdown.

## Features

- Browse and search debate topics
- Sign up, sign in, and view your topics and comments
- Create topics with custom voting sides and an optional end date
- Vote once per topic while voting is open, with a written explanation
- View vote totals and comments on each topic
- Edit or delete topics you created

## Run locally

From the repository root:

```bash
cd ProjectFiles
python -m venv .venv
source .venv/bin/activate
python -m pip install Django
python manage.py migrate
python manage.py runserver
```

On Windows, activate the environment with `.venv\Scripts\activate` instead. Then open <http://127.0.0.1:8000/>.

The app uses SQLite by default. The database file is created locally and is excluded from Git.

## Main app structure

- `ProjectFiles/debates/` contains debate models, views, forms, templates, and migrations.
- `ProjectFiles/debate_project/` contains Django project settings and URL configuration.
