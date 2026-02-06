FROM mongo:latest

# Copy the wrapper script that handles initialization
COPY mongo-dump/docker-entrypoint-wrapper.sh /usr/local/bin/

# Set executable permission
RUN chmod +x /usr/local/bin/docker-entrypoint-wrapper.sh

# Copy database dump files
COPY mongo-dump/research_db_structure /docker-entrypoint-initdb.d/research_db_structure/

# Use the wrapper script as entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
