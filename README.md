## Assignment link → https://simplismart.notion.site/Infrastructure-Engineer-Assignment-4d63a3d980c04b82b2d06ea857aa1e62

## Submission guidelines
1. Your output should be a GitHub repo link or a zip file.
2. Provide a clear README with instructions, assumptions, and API details.
3. Include unit tests and instructions to run them.
4. Highlight any extra features added beyond the requirements.
5. Send over your output on email to madhav@flexiple.com, marking hrishikesh@flexiple.com in cc

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