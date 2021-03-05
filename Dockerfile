FROM python

WORKDIR /usr/src/zirkusmond
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD . .
COPY manage.py ..

RUN python ../manage.py makemigrations
RUN python ../manage.py makemigrations events
RUN python ../manage.py migrate
RUN python ../manage.py collectstatic
EXPOSE 8000
CMD ["python", "../manage.py", "runserver", "0.0.0.0:8000"] 
