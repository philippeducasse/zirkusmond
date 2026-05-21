

- html_base
  - index includes containers.html
  - html_design (block content)
    - show
      - event (replace block show_details)


- container_basic 
    - container_gallery
    - container_team
    - container_stream
    - container_last
- container_base extended by

## Tailwind watcher

run it in frontend/

npm run tailwind 


## TODO

- Change logos in zm- ->> border radius on lisboa
- change images
- add Merch in navbar -> redirect to payment site


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
- Password: `iR2#,z,l`

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
 - make sure newsletter subsciptions have been exported. this table will be wiped clean
 - make sure to git clone into a fresh repo / folder -> git clone -b organise-backend git@git.ableph.net:ableph/zirkusmond_de.git ~/
 - make sure env file is correctly defined