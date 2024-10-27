#!/bin/sh
set -e

# # Call the original entrypoint script
# /usr/local/bin/docker-entrypoint.sh postgres &

# # Wait for PostgreSQL to start
# until pg_isready; do
#     sleep 1
# done

# /usr/local/bin/init.db.sh &

# # Keep the container running
# wait $!



# Run the original entrypoint script, but don't start PostgreSQL yet
eval "$(grep ^exec /usr/local/bin/docker-entrypoint.sh | sed 's/^exec//')" &

# Wait for PostgreSQL to start
until pg_isready; do
    sleep 1
done

# Run your initialization script
/usr/local/bin/init.db.sh

# Now start PostgreSQL in the foreground
exec postgres