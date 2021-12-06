# UWB_2FA
CS8803: Mobile Computing &amp; IOT Project

Link for Beta PDOA Kit Release for Deca DWM1002 and DWM1003 
https://drive.google.com/file/d/1pWX6p5T-vz_O6ybLb7ILc3TRKaeQPOsl/view?usp=sharing

## Contributors
Saket Singh and Niraj Srimal. Special thanks to [Prof. Dhekne](https://www.cc.gatech.edu/~dhekne/) for guidance!

## Prerequisites
- You need Angular CLI installed. 
- First install node: https://nodejs.org/en/download/
- Use node's package manager to install Angular CLI: https://angular.io/cli

## Starting the UI
After setting up, run these relative to the project root.

```shell
cd ./FrontEnd

# Required once / if more dependencies are added 
npm i

# This does hot reloads, so run once and forget
npm start

# OPTIONAL: To install modules you might want to use
npm install --save [module_name]
```

## Starting the backend
We need the server running for the UI to send requests. I've currently redacted the firestore keys which are required for the sign up and sign in flow. 

```shell
cd ./BackEnd

# Create a venv however you'd like, and switch profiles to it
pip install -r requirements.txt

python server.py 
```

