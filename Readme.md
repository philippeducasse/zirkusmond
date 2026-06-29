


- translations: en, de, es, pt


## FAQ

    python manage.py makemigrations
    python manage.py migrate
    python manage.py shell
    python manage.py sqlmigrate 0001

    pip install django-markdownx
    python3 manage.py collectstatic

    pip install markdown

https://docs.djangoproject.com/en/3.1/intro/tutorial02/
https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.ForeignKey.on_delete

https://learndjango.com/tutorials/django-markdown-tutorial
https://django-markdownify.readthedocs.io/en/latest/install_and_usage.html

https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax

## docker

Build from project root:

    sudo docker build -t zirkusmond .
    sudo docker run --name zirkusmond -p 9000:8000 zirkusmond
    sudo docker exec -it zirkusmond /bin/bash


## payment testing

### sofort

8x 8
7x 7
1234

### paypal

- User: `sb-f2wjp5409330@business.example.com`
- Password: iR2#,z,l

### stripe

Use any card listed in the Stripe docs https://docs.stripe.com/testing#cards. Common example:

- Card: `4242 4242 4242 4242`
- Expiry: any future month/year (e.g. `12 / 34`)
- CVC: any 3 digits (e.g. `123`)
- ZIP: any 5 digits (e.g. `12345`)


### Todos philo 2026:
- fix person / guest classes

# deploy code

cd test_zirkus_mond
(... here you probably have to vim .git/config and change your user, add your api key)
git switch -c yourbranch yourbranch
sudo docker-compose build zirkusmond
sudo docker-compose stop zirkusmond
sudo docker-compose up zirkusmond

# qr code duplication
# cookie popover
# remove talent && venue && remove all other emails from website
# add way for juan to change videos && images
# handle case for shows that zm doesnt handle bookings

# early bird tickets
# tickets umbuchen

  # Notes to migrate to new architecture:
  - docker exec ubuntu-zm_db-1 pg_dump -U mond monddb > ~/zirkusmond_latest.sql
  - make sure newsletter subscriptions have been exported — this table will be wiped clean
  - make sure env file is correctly defined
  - git switch organise-backend in zirkusmond_de
  - rebuild containers: docker compose up -d --build --remove-orphans
  - docker-compose.yml: zm_db service renamed to postgres (old line commented out for easy revert)

  
  ## If something goes wrong — full rollback
  
  1. Switch code back:
     cd ~/zirkusmond_de && git switch main

  2. Revert docker-compose.yml — swap the postgres/zm_db comments back
  
  3. Stop the app, keep DB running:
     docker compose stop zirkusmond_de

  4. Drop and restore the database:
     docker exec ubuntu-zm_db-1 psql -U mond -c "DROP DATABASE monddb WITH (FORCE);"
     docker exec ubuntu-zm_db-1 psql -U mond -c "CREATE DATABASE monddb OWNER mond;"
     docker exec -i ubuntu-zm_db-1 psql -U mond monddb < ~/zirkusmond_backup.sql
  
  5. Rebuild and restart:
     docker compose up -d --build

