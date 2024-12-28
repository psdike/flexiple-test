## Install minikube
brew install minikube

## Install Helm
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3; 
chmod 700 get_helm.sh;
./get_helm.sh
```
## Create python env and activate it
```
python3 -m venv test-env
source test-env/bin/activate
```
## Run pip config

`pip3 install kubernetes pyyaml`

## Finally run main program
`python3 main.py`