# syntax=docker/dockerfile:1.4
# Multi-stage build to support multiple architectures
 
# Builder stage: Build ArduPilot
FROM --platform=$BUILDPLATFORM ubuntu:22.04 AS builder
LABEL stage=ardupilot-sitl-builder
 
# Define build arguments for non-interactive installations and user details
ARG DEBIAN_FRONTEND=noninteractive
ARG USER_NAME=ardupilot
ARG USER_UID=1000
ARG USER_GID=1000
 
# Create a user group and user with specified UID and GID
RUN groupadd ${USER_NAME} --gid ${USER_GID} \
    && useradd -l -m ${USER_NAME} -u ${USER_UID} -g ${USER_GID} -s /bin/bash
 
# Define the tag for the ArduPilot version to check out
ARG COPTER_TAG=Rover-4.5
 
# Install git and other necessary dependencies
RUN apt-get update && apt-get install -y \
    git \
    lsb-release \
    sudo \
    tzdata \
    bash-completion \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    wget \
    unzip \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-numpy \
    python3-pyparsing \
    python3-psutil \
    && git config --global url."https://github.com/".insteadOf git://github.com/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
 
# Clone the ArduPilot repository from GitHub
RUN git clone https://github.com/ArduPilot/ardupilot.git /home/${USER_NAME}/ardupilot
WORKDIR /home/${USER_NAME}/ardupilot
 
# Checkout the specified tag for ArduPilot
RUN git checkout ${COPTER_TAG}
 
# Update all git submodules
RUN git submodule update --init --recursive
 
# Set up sudoers file for the non-root user to allow passwordless sudo
RUN echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USER_NAME} \
    && chmod 0440 /etc/sudoers.d/${USER_NAME} \
    && chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}
 
# Add the user to the dialout group for serial port access
RUN usermod -aG dialout ${USER_NAME}
 
# Switch to the created user
USER ${USER_NAME}
 
# Set environment variables to skip certain setup steps
ENV SKIP_AP_EXT_ENV=1
ENV SKIP_AP_GRAPHIC_ENV=1
ENV SKIP_AP_COV_ENV=1
ENV SKIP_AP_GIT_CHECK=1
 
# Install each package individually to isolate the problem
RUN pip3 install --user -U future
RUN pip3 install --user -U lxml
RUN pip3 install --user -U pymavlink
RUN pip3 install --user -U pyserial
RUN pip3 install --user -U MAVProxy
RUN pip3 install --user -U pexpect
RUN pip3 install --user -U geocoder
RUN pip3 install --user -U empy==3.3.4
RUN pip3 install --user -U ptyprocess
RUN pip3 install --user -U dronecan
RUN pip3 install --user -U flake8
RUN pip3 install --user -U junitparser
 
# Copy the install script and modify it to skip adding the user to the dialout group
RUN cp Tools/environment_install/install-prereqs-ubuntu.sh Tools/environment_install/install-prereqs-ubuntu-mod.sh \
    && sed -i '/usermod -a -G dialout/d' Tools/environment_install/install-prereqs-ubuntu-mod.sh
 
# Install prerequisites using the modified script
RUN Tools/environment_install/install-prereqs-ubuntu-mod.sh -y
 
# Clean and configure the ArduPilot build
RUN ./waf distclean && ./waf configure --board sitl
 
# Build ArduPilot components in smaller steps
RUN ./waf copter
RUN ./waf heli
RUN ./waf plane
RUN ./waf rover
RUN ./waf sub
 
# Pip installer stage: Create a new stage for installing Python packages
FROM --platform=$BUILDPLATFORM python:3.10-slim AS pip_installer
LABEL stage=ardupilot-sitl-pip-installer
WORKDIR /app
 
# Install necessary dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
 
# Upgrade pip and install required Python packages
RUN pip install --upgrade pip
RUN pip install pexpect pymavlink
 
# Final stage: Create the final image for running ArduPilot SITL
FROM --platform=$TARGETPLATFORM python:3.10
ARG USER_NAME=ardupilot
ARG USER_UID=1000
ARG USER_GID=1000
 
# Install necessary system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
 
# Copy the built ArduPilot files and Python packages from the previous stages
COPY --from=builder /home/ardupilot/ardupilot /ardupilot
COPY --from=pip_installer /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
 
# Expose TCP port 5760, which the simulator uses by default
EXPOSE 5760/tcp
 
# Set default environment variables for the simulator
ENV INSTANCE="0"
ENV VEHICLE="Rover"
ENV MODEL="rover-skid"
ENV HOME_POS="57.760813, 16.683194, 34, 75"
ENV SPEEDUP="1"
ENV VEHICLE_PARAMS="Rover"
 
# Copy parameter files to the appropriate location
#COPY params/my*.params /ardupilot/Tools/autotest/default_params/
#COPY params/my*.params /params/.
 
# Define the entry point for the container
# ENTRYPOINT /ardupilot/Tools/autotest/sim_vehicle.py --vehicle ${VEHICLE} --frame ${MODEL} -I${INSTANCE} --custom-location=${HOME_POS} --add-param-file=/ardupilot/Tools/autotest/default_params/my${VEHICLE}.params -w --no-rebuild --no-mavproxy --speedup ${SPEEDUP}
# ENTRYPOINT ["/ardupilot/Tools/autotest/sim_vehicle.py", "--vehicle", ${VEHICLE}, "--frame", "${MODEL}", "-I", "${INSTANCE}", "--custom-location=${HOME_POS}", "--add-param-file=/ardupilot/Tools/autotest/default_params/my${VEHICLE}.params", "-w", "--no-rebuild", "--no-mavproxy", "--speedup", "${SPEEDUP}"]
# ENTRYPOINT ["/bin/bash", "-c", "/ardupilot/Tools/autotest/sim_vehicle.py --vehicle ${VEHICLE} --frame ${MODEL} -I${INSTANCE} --custom-location=${HOME_POS} --add-param-file=/ardupilot/Tools/autotest/default_params/my${VEHICLE}.params -w --no-rebuild --no-mavproxy --speedup ${SPEEDUP}"]
ENTRYPOINT ["/bin/bash", "-c", "/ardupilot/Tools/autotest/sim_vehicle.py --vehicle ${VEHICLE} --frame ${MODEL} -I${INSTANCE} --custom-location=${HOME_POS} --add-param-file=/params/my${VEHICLE_PARAMS}.params -w --no-rebuild --no-mavproxy --speedup ${SPEEDUP}"]