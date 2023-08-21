FROM nialljb/njb-ants-fsl-base:0.0.1 as base

ENV HOME=/root/
ENV FLYWHEEL="/flywheel/v0"
WORKDIR $FLYWHEEL
RUN mkdir -p $FLYWHEEL/input

# Installing the current project (most likely to change, above layer can be cached)
COPY ./ $FLYWHEEL/

# Dev dpendencies
RUN apt-get update && apt-get install --no-install-recommends -y software-properties-common=0.96.20.2-2 && \
    apt-get clean && \
    pip3 install flywheel-gear-toolkit && \
    pip3 install flywheel-sdk && \
    pip3 install importlib_metadata && \
    pip3 install pandas && \
    apt-get update && apt-get install jq -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installing main dependencies
RUN git clone https://github.com/MIC-DKFZ/HD-BET && \
    cd HD-BET && \
    pip3 install -e .  
    
# Configure entrypoint
ENTRYPOINT ["python3","/flywheel/v0/run.py"] 
# Flywheel reads the config command over this entrypoint