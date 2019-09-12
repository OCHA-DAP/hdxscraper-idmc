### Collector for IDMC's Datasets
[![Build Status](https://travis-ci.org/OCHA-DAP/hdx-scraper-idmc.svg?branch=master&ts=1)](https://travis-ci.org/OCHA-DAP/hdx-scraper-idmc) [![Coverage Status](https://coveralls.io/repos/github/OCHA-DAP/hdx-scraper-idmc/badge.svg?branch=master&ts=1)](https://coveralls.io/github/OCHA-DAP/hdx-scraper-idmc?branch=master)

This script connects to the [IDMC API](https://api.idmcdb.org/) and extracts data for 2 endpoints country by country creating a dataset per country in HDX. It makes 2 reads from IDMC and 1000 read/writes (API calls) to HDX in a one hour period. It creates around 500 temporary files each a few Kb which it uploads into HDX. It is run every year.


### Usage

    python run.py

For the script to run, you will need to have a file called .hdx_configuration.yml in your home directory containing your HDX key eg.

    hdx_key: "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hdx_read_only: false
    hdx_site: prod
    
 You will also need to supply the universal .useragents.yml file in your home directory as specified in the parameter *user_agent_config_yaml* passed to facade in run.py. The collector reads the key **hdx-scraper-idmc** as specified in the parameter *user_agent_lookup*.
 
 Alternatively, you can set up environment variables: USER_AGENT, HDX_KEY, HDX_SITE, EXTRA_PARAMS, TEMP_DIR, LOG_FILE_ONLY
