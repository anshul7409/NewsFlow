# NEWSFLOW 

**Efficient News summarization with MAP Reduce AND Clustering Methodology**

## Description

**NewsFlow** is the Efficient summarization framework which summarizes Large Textual Data with Map reduce and Clustering Framework. Map reduce and clustering is implemented as a high-level concept here for serving unique purpose of summarization.

**Workflow**:
* *Dataset preparation* : Combined well known news datasets with our custom dataset for training model for efficient summarization.
* *Data Fetching API* : Created custom API for data fetching and retrieval from multinews sources. Collected all news in No-SQL database.
* *MAP reduce Framework* : This module divides the huge data into chunks based on the importance.
* *Transformer model* : Fine Tune pretrained Transformer model, for summarization ofdata chunks. This model ensures efficient summarization of clusters.
* *Model Deployment* : Hosted the model using Flask API.
* *End-to-End demo* : end-to-end web application for showcase.

![image](https://github.com/anshul7409/NewsFlow/assets/79444489/eb27bc02-f906-4577-9146-9c22e835e80d)

## Getting Started

### MODEL API serving

#### Dependencies
* download dependencies
```
pip install -r requirements.txt
```

#### Executing program
* Go to NewFlow Folder
```
cd /'Newsflow API'
```
* Run Flask Server
```
flask --app Model_api  run --debug                                                                                               
```

### Running demo App

#### Dependencies
* Go to demo Folder
```
cd /'demo'
```
* download dependencies
```
npm install 
```

#### Executing program
* Run App
```
npm run dev                                                                                         
```

# DEMO APP
![image](https://github.com/anshul7409/NewsFlow/assets/79444489/11abf5a3-9f6a-4b3f-8d45-eed2bc9a4795)

# Model Performance Metrics

![image](https://github.com/anshul7409/NewsFlow/assets/79444489/3f9e8306-a10d-4f7b-99f9-82c5fa722f7f)


## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)


## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
