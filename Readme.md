

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

