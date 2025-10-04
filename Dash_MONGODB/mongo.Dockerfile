FROM mongo:latest

# Copy initialization scripts
COPY mongo-dump/docker-entrypoint-wrapper.sh /usr/local/bin/
COPY mongo-dump/init-db.sh /docker-entrypoint-initdb.d/

# Set executable permissions
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh \
    /docker-entrypoint-initdb.d/init-db.sh

# Copy database dump files
COPY mongo-dump/research_db_structure /docker-entrypoint-initdb.d/research_db_structure/

# Use the wrapper script as entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
