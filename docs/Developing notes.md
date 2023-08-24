# Developing notes

10/08/2023
SVTK docker image built from source as a base image with the Flywheel structure:
*FROM fetalsvrtk/svrtk:auto-2.20 as base*

- folder structure including:
- manifest
- Dockerfile
- run.py

> docker build -t nialljb/fw-svrtk-base . 


Initital viewing of container:
> docker run -it --rm --entrypoint bash nialljb/fw-svrtk-base

mirtk tools are present but not sourced

There are a number of tools available inside the container. Will begin with 
> /home/auto-proc-svrtk/auto-brain-reconstruction.sh

as this can be called easily, just need to wrap and organise sourcing input/. 
Haven't worked out why/how to source other mritk tools yet. 