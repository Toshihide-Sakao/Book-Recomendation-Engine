# Book-Recomendation-Engine
**To run the app:**

***OBS! You need to first start Elasticsearch locally***

***Then:***

1. pip -r requirements.txt
2. create a file with name "config_template.info" at root directory with following contents:
- DEFAULT
- es_username=elastic
- es_password= PUT YOUR PASSWORD
- index_name=books
3. run the command: python backend_template.py