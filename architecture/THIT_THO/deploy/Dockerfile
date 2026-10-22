FROM python:3.12-slim
WORKDIR /srv
COPY web/ /srv/web/
COPY data/schema/001_er.sql /srv/schema/001_er.sql
RUN mkdir -p /srv/data && python -c "import sqlite3,pathlib; p=pathlib.Path('/srv/data/er.sqlite3'); c=sqlite3.connect(p); c.executescript(pathlib.Path('/srv/schema/001_er.sql').read_text()); c.commit(); c.close()"
RUN useradd --uid 10001 --create-home tesseract && chown -R tesseract:tesseract /srv/data
USER tesseract
EXPOSE 8765
CMD ["python","/srv/web/backend/server.py","--db","/srv/data/er.sqlite3","--host","0.0.0.0","--port","8765","--container"]
