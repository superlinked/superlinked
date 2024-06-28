#!/bin/bash
# please install pyenv, poetry on your system
# on Mac
# brew install pyenv
# brew install poetry

set -euxo pipefail

script_path=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
cd "${script_path}/../runner/"

eval "$(pyenv init --path)"

python_version=$(cat ../.python-version)

if ! pyenv versions | grep -q "${python_version}"; then
    echo y | pyenv install "${python_version}"
fi

poetry env use $(pyenv local ${python_version} && pyenv which python)

<<<<<<< HEAD
<<<<<<< HEAD
=======
poetry cache list | awk '{print $1}' | xargs -I {} poetry cache clear {} --all

>>>>>>> 6749add (server/1.12.0)
=======
poetry cache list | awk '{print $1}' | xargs -I {} poetry cache clear {} --all

>>>>>>> 9035a87 (server/1.12.1)
poetry install --no-root --with poller,executor,dev

source "$(poetry env info --path)/bin/activate"
