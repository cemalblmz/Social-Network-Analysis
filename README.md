# Social-Network-Analysis
Node Classification - Representation Learning - Node2vec - Random Forest - Logistic Regression - PCA -TSNE

Nodes represent official Facebook pages while the links are mutual likes between sites. Node features are extracted from the site descriptions that the page owners created to summarize the purpose of the site. This graph was collected through the Facebook Graph API in November 2017 and restricted to pages from 4 categories which are defined by Facebook. These categories are: politicians, governmental organizations, television shows and companies. The task related to this dataset is multi-class node classification for the 4 site categories.


The the task of the notebook is to apply node classification on Facebook network Data.

Original Paper Provides Data Set: https://arxiv.org/abs/1909.13021

Data Source: Stanford Network Analysis Project

Data Date: 2017

Type: Webgraph

Topic: Facebook Pages

Node Features: Page Names (unique), Facebook ID of pages (unique), Page Category (4 Contents; 
politicians, governmental organizations, television shows and companies)

Edges: Undirected, Mutual likes between sites (171,002 edges)

Dataset statistics

Directed	No.

Node features	Yes.

Edge features	No.

Node labels	Yes. Binary-labeled.

Temporal	No.

Nodes	22,470

Edges	171,002

Density	0.001

Transitvity	0.232

B. Rozemberczki, C. Allen and R. Sarkar. Multi-scale Attributed Node Embedding. 2019.

          @misc{rozemberczki2019multiscale,
            title={Multi-scale Attributed Node Embedding},
            author={Benedek Rozemberczki and Carl Allen and Rik Sarkar},
            year={2019},
            eprint={1909.13021},
            archivePrefix={arXiv},
            primaryClass={cs.LG}
        }
        
          
