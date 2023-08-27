# Real Estate Analysis


```
sh
python3 -m pip install --upgrade pip 
```

# Installation

1. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```
    
4. Update pip


    ```
    python3 -m pip install --upgrade pip 
    ```

## Running the Script

1. Run the script to get all Links:
    
    ```bash
    python scrap_all_links.py --url 'https://www.vivareal.com.br/aluguel/santa-catarina/sao-jose/bairros/kobrasol/apartamento_residencial/#onde=Brasil,Santa%20Catarina,S%C3%A3o%20Jos%C3%A9,Bairros,Kobrasol,,,,BR%3ESanta%20Catarina%3ENULL%3ESao%20Jose%3EBarrios%3EKobrasol,,,&preco-ate=2500&preco-total=sim' --filename aluguel_kobrasol
   ```
   - url: Link to the webpage you want to scrape the links.
   - filename: name of the csv file containing all the links.
2. Run the Script to get features from each link in the CSV File. 
    ```bash
    scrap_individually.py
   ```

3. 