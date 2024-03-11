# Start from a Miniconda base image
FROM continuumio/miniconda3

# Create a Conda environment and install pyOCC
RUN conda create -n pyocc python=3.8 && \
    echo "source activate pyocc" > ~/.bashrc && \
    /bin/bash -c "source activate pyocc && \
    conda install -c conda-forge pythonocc-core"
