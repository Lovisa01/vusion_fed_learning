# BlueLLMTeam
Blue team of LLM agents that can use honeypots to defend resources against a red team

# Deploy
To deploy and run automatically in AWS follow these steps.
```bash
# Clone git repository
git clone git@github.com:Lovisa01/vusion_fed_learning.git

# cd into the repository
cd vusion_fed_learning

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e BlueLLMTeam
```

To automatically start the project when the AWS instance runs, setup a systemctl script

```bash
# Create and modify the start script for the application
sudo vim /etc/systemctl/system/blue-llm-team.service

# Automatically start it
sudo systemctl daemon-reload
sudo systemctl start blue-llm-team
sudo systemctl enable blue-llm-team
```

Look at the logs from it with 
```bash
# Look at all logs
sudo journalctl -u blue-llm-team.service

# Look at the logs in realtime
sudo journalctl -u blue-llm-team.service -f
```

