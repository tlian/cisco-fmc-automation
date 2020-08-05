# CISCO Firepower Management Console (FMC) REST API Utility

Interact with FMC's REST api.

### How to setup FMC virtual environment

1. Spin up FMC sandbox in Cisco. 

(Note that Cisco account is required to make reservation below. Account creation is FREE).

 * FMC sandbox can be reserved at Cisco. Click on "Firepower Management Center" in the following link.
   https://developer.cisco.com/docs/sandbox/#!security/featured-sandboxes
 * Click on "RESERVE" button found at top right corner. 
 * Username and Password will be emailed to your email address.


### INSTALLATION

Recommendation is to install it in Python virtual environment (pyenv)

1. Install pyenv and pyenv-virtualenv

   ```
   brew install pyenv pyenv-virtualenv
   echo "export PATH=$HOME/.pyenv/bin:$PATH >> ~/.zshrc
   echo "eval $(pyenv init -)" >> ~/.zshrc
   echo "eval $(pyenv virtualenv-init -)" >> ~/.zshrc
   ```
2. Install Python-3.7.5

   ```pyenv install 3.7.5```
3. Create virtual environment

   ```pyenv virtualenv 3.7.5 venv375```
4. Activate virtual environment

   ```pyenv activate venv375```
5. Install cisco-fmc-modules package

   ```
   git clone https://github.com/tlian/cisco-fmc-automation
   cd cisco-fmc-automation
   pip install .
   ```

### EXAMPLE

Note: Make sure /var/log/ is accessible by the running user before running the following script. Else, quick do...
```
touch /var/log/fmc_automation.log
chown user:admin /var/log/fmc_automation.log
```

```
# Create FTD NAT Policy
avi-nat --fmchost $FMC_LAB_HOST -u $FMC_LAB_USERNAME -p $FMC_LAB_PASSWORD --create-ftdnatpolicy "TD_nat_policy"

# Create Host object (i.e. New VIP IP)
avi-create-object --fmchost $FMC_LAB_HOST -u $FMC_LAB_USERNAME -p $FMC_LAB_PASSWORD --name test_avi_vip --object-type hosts --network 1.1.2.2

# Create Public IP (i.e. In AVI migration, will probably use existing one.)
avi-create-object --fmchost $FMC_LAB_HOST -u $FMC_LAB_USERNAME -p $FMC_LAB_PASSWORD --name public_vip_ip --object-type hosts --network 172.4.4.4

# Create Auto NAT Rule 
avi-nat --fmchost $FMC_LAB_HOST -u $FMC_LAB_USERNAME -p $FMC_LAB_PASSWORD --create-autonatrule '{"targetNatPolicy": "TD_nat_policy", "sourceInterface": "inside-zone", "destinationInterface": "outside-zone", "originalNetwork": "test_avi_vip", "translatedNetwork": "public_vip_ip", "natType": "STATIC"}'
```

### Docker image
Note: Docker image for cisco-fmc-tool has been created and pushed to harbor. To see how to push and use the latest image, please refer to the doc: <br/>
 - [Using Docker Image](./docs/docker-fmc.md)
