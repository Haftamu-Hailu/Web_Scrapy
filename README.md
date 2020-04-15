# Cloud Computing Lab 7

## Task 7.3: Study the obtained data using the Elastic Stack

After we scraped the data we analyze it using the **elastic stack software** which is a collection of three major components  which are Elasticsearch, Logstash, and Kibana<br/>
1. Logstash-  tool for managing events and logs
2. Elasticsearch-a document-oriented NoSQL database designed to store, retrieve and manage structured and semi-structured data.
3. Kibana- is data visualization and exploration tool 

Therefore in our configuration we use Logstash to send the data into Elasticsearch where the data is get indexed and Kibana to visualize the json data to drive insights.  
## Logistach configuration file to send data into an Elasticssearch  Index.

![](configuration.PNG)

