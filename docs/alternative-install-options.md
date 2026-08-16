# Alternative install options for using `cffconvert`

## Install in virtual environment

The official interim source distribution is the Git tag attached to a published GitHub Release.
The first planned concrete example is `v2026.08`. `main` is development-only, and PyPI is not the distribution channel
for this fork.
Replace `<release-tag>` with the published GitHub Release tag in the commands below.

```shell
# use venv to make a virtual environment named venv
python3 -m venv venv

# activate the environment
source venv/bin/activate

# install cffconvert from the published release tag
pip install git+https://github.com/scicodes/cffconvert.git@<release-tag>
```

## Install globally

Note: this option needs sudo rights.

```shell
sudo -H python3 -m pip install git+https://github.com/scicodes/cffconvert.git@<release-tag>
```

## Install with conda

Make an environment definition file `environment.yml` with the following contents:

```yaml
name: venv
channels:
  - conda-forge
  - defaults
dependencies:
  - pip
  - pip:
    - git+https://github.com/scicodes/cffconvert.git@<release-tag>
```

Then run:

```shell
conda env create --file environment.yml
conda activate venv
```

## No-install options

### Using `cffconvert` as a Google Cloud Function

`cffconvert` comes with [an interface](../src/cffconvert/gcloud/gcloud.py) for
running as a Google Cloud Function.

Really, all the Google Cloud interface does is get any supplied URL
parameters, and use them as if they had been entered as command line
arguments.

On Google Cloud Function, set `requirements.txt` to:

```text
cffconvert[gcloud]
```

and use the following as `main.py`:

```python
from cffconvert.gcloud.gcloud import cffconvert

def main(request):
   return cffconvert(request)
```

### Docker

Build the Docker container 

```shell
cd <project root>
docker build --tag cffconvert:3.0.0a0 .
docker build --tag cffconvert:latest .
```

Run the Docker container 

```shell
cd <where your CITATION.cff is>
docker run --rm -ti -v ${PWD}:/work -w /work cffconvert
```

### Platform-specific packages

#### Alpine Linux

To install cffconvert on Alpine Linux, use:

```sh
apk add cffconvert
```

#### Fedora Linux

To install cffconvert on Fedora Linux, use:

```sh
dnf install cffconvert
```
