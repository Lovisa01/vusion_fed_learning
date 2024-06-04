# Use the official Ubuntu base image
FROM ubuntu:latest

# Update and install dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git python3-virtualenv libssl-dev libffi-dev build-essential libpython3-dev python3-minimal authbind virtualenv iptables

# Create a new user 'cowrie' with no password
RUN adduser --disabled-password --gecos "" cowrie

# Switch to user 'cowrie'
USER cowrie
WORKDIR /home/cowrie

# Download and setup Cowrie
RUN git clone https://github.com/iamfareedshaik/cowrie.git && \
    cd cowrie && \
    virtualenv cowrie-env && \
    . cowrie-env/bin/activate && \
    pip install --upgrade pip && \
    pip install --upgrade -r requirements.txt

# Copy the default configuration
RUN cp cowrie/etc/cowrie.cfg.dist cowrie/etc/cowrie.cfg

# # Set up iptables for redirecting ports
# USER root
# RUN iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222 && \
#     iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223


# USER cowrie
EXPOSE 2222 2223

# Start Cowrie
CMD ["cowrie/bin/cowrie", "start", "-n"]
