# -*- coding: utf-8 -*-
"""Facebook Network Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fHeerFb5X9bEYlvaH4BCeVZrGTl0GPP3
"""

import pandas as pd
import networkx as nx
#import graph_tool.all as gt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter
from node2vec import Node2Vec
from random import sample
from sklearn import model_selection as mod
from sklearn import preprocessing as pre
from sklearn import pipeline as pip
from sklearn import manifold as man
from sklearn import linear_model as lin
from sklearn import decomposition as dec
from sklearn import impute as imp
from sklearn import ensemble as ens
from sklearn import metrics as met
from sklearn import compose as com
import matplotlib.cbook
from sklearn.model_selection import learning_curve

nx.__version__

"""# Reading The Data"""

# https://snap.stanford.edu/data/facebook-large-page-page-network.html

df = pd.read_csv('musae_facebook_target.csv')
df.head()

df2 = pd.read_csv('musae_facebook_edges.csv')#.set_index('id').transpose().to_dict()
df2.head()

"""# Subgroups"""

count_dict = {}
for row in df2.itertuples():
    if row.id_1 not in count_dict:
        count_dict[row.id_1] = 1
    else:
        count_dict[row.id_1] += 1
    if row.id_2 not in count_dict:
        count_dict[row.id_2] = 1
    else:
        count_dict[row.id_2] += 1

df["counts"] = df.index.map(count_dict)
df.head()

df.sort_values(by=["counts"], ascending=False).head(20)

plt.figure(figsize=(25,10))
plt.subplot(2,3,1)
sns.distplot(df.counts)
plt.title("degree")
plt.xlabel("Degree")

t = 2 
for i in df.page_type.unique():
    plt.subplot(2,3,t)
    sns.distplot(df[df.page_type == i]["counts"])
    plt.title(i)
    plt.xlabel("Degree")

    t += 1
plt.show()

plt.figure(figsize=(25,10))
ax=sns.catplot(x="counts", y="page_type", hue="page_type",kind="box",height=4, aspect=4, orient="h", data=df, palette="rocket")
plt.xlabel("Degree")
plt.show()

"""> Degree of government pages tend to be higher than others

# Network Analysis
"""

df.drop(columns=["facebook_id","page_name","counts"],axis=1,inplace=True)
df.head()

tvshow_ratio    = (str(round(df[df["page_type"] == "tvshow"]["page_type"].count()/df["page_type"].count(),2)*100))
government_ratio = (str(round(df[df["page_type"] == "government"]["page_type"].count()/df["page_type"].count(),2)*100))
company_ratio   = (str(round(df[df["page_type"] == "company"]["page_type"].count()/df["page_type"].count(),2)*100))
politician_ratio   = (str(round(df[df["page_type"] == "politician"]["page_type"].count()/df["page_type"].count(),2)*100))
sns.set_style("white")
plt.figure(figsize=(10,7))
sns.countplot(x='page_type', data=df, palette="Set1")
plt.title("tvshow: "+ tvshow_ratio + " - government: " + government_ratio +  " - company: " + company_ratio+" - politician: "+politician_ratio)
plt.show()

"""Classes are not perfectly balanced"""

G = nx.from_pandas_edgelist(pd.read_csv('musae_facebook_edges.csv', header=0, names = ['source', 'target']), create_using=nx.Graph())

node_attributes = df.set_index('id').transpose().to_dict()

nx.set_node_attributes(G, node_attributes)
G.nodes(data=True)

print(nx.info(G))
print()
print("Has Eulerian path: ", nx.has_eulerian_path(G))
print()
print("Is bipartite: ", nx.is_bipartite(G))
print()
#print("Degrees: ", nx.degree(G))
print()
print("Density: ", nx.density(G))
highest_degree_node = max(G.nodes, key=G.degree)
print()
print("Node",highest_degree_node, "has the highest degree and the degree is", G.degree(highest_degree_node))
print()
# If the network is disconnected, shortest path will raise errror. Therefore, I will use try/except.
print("Number of connected components: ",nx.number_connected_components(G))
print("The list of componensts:",list(nx.connected_components(G)))
print()
print("\n"*3)

"""- Network seems quite sparse. Density is 0.0007
- It is connected
"""

t = 1
list_clique = []
counter = 0
for i in nx.find_cliques(G):
    list_clique.append(i)
    counter += 1
print()
print("There are",counter,"cliques in the network")

degrees = pd.DataFrame(G.degree,columns=["Nodes","Degree"])
plt.figure(figsize=(20,7))
plt.subplot(1,2,1)
degree_counts = pd.DataFrame(degrees.groupby(["Degree"]).size().reset_index())
p1 = sns.barplot(x=degree_counts.iloc[:,0],y=degree_counts.iloc[:,1],color="r")
plt.title("Degree Distribution")
plt.ylabel("Count")
p1.set(xticklabels=[])

plt.subplot(1,2,2)
degree_counts = pd.DataFrame(degrees.groupby(["Degree"]).size().reset_index())
p2 = sns.barplot(x=round(np.log(degree_counts.iloc[:,0]),3),y=np.log(degree_counts.iloc[:,1]),color="r")
plt.title("Degree Distribution to check powerlaw")
plt.ylabel("Count")
p2.set(xticklabels=[])
plt.show()

"""network follows powerlaw"""

dgc = nx.degree_centrality(G)
eig = nx.eigenvector_centrality(G)
#ktz = nx.katz_centrality(G)
pgr = nx.pagerank(G)
btw = nx.betweenness_centrality(G)
cr = pd.DataFrame(index=G.nodes())
cls = nx.closeness_centrality(G)

#cr['katz'] = cr.index.map(ktz)
cr['pagerank'] = cr.index.map(pgr)
cr['closeness_centrality'] = cr.index.map(cls)
cr['degree'] = cr.index.map(G.degree())
cr['degree_centrality'] = cr.index.map(dgc)
cr['eigenvector_centrality'] = cr.index.map(eig)
cr['betweenness_centrality'] = cr.index.map(btw)
cr['clustring_coef']= cr.index.map(nx.clustering(G))
cr['eigenvector_centrality'] = round(cr.eigenvector_centrality,4)

t = 1
list_clique = []
counter = 0
for i in nx.find_cliques(G):
    list_clique.append(i)
    counter += 1
print()
print("There are",counter,"cliques in the network")

clique_num_each_node = {}
for j in range(len(list_clique)):
    for i in range(len(list_clique[j])):
        key = list_clique[j][i]
        if key not in clique_num_each_node:
            clique_num_each_node[key] = 1
        else: 
            clique_num_each_node[key] += 1

number_of_cliques = pd.DataFrame([clique_num_each_node]).T
number_of_cliques =  number_of_cliques.rename(columns={0:"number_of_cliques"})
print(number_of_cliques.shape)
print(cr.shape)
number_of_cliques.head()

cr = cr.merge(number_of_cliques,left_index=True, right_index=True)

size_maximal_clique = {}
for i in list(G.nodes()):
    num = nx.algorithms.clique.node_clique_number(G, nodes=i, cliques=None)
    if i not in size_maximal_clique:
        size_maximal_clique[i] = num

cr["size_maximal_clique"] = cr.index.map(size_maximal_clique)

cr.to_excel("cr.xlsx")

cr = pd.read_excel("cr.xlsx",index_col=0)

plt.figure(figsize=(8,5))
sns.distplot(cr['number_of_cliques'],kde=True,)
plt.show()

#Centralities of the nodes
t = 1
plt.figure(figsize=(20,15))
for i in cr.columns:
    plt.subplot(2,3,t)
    sns.barplot(x=cr.index,y=cr[i])
    t += 1
plt.show()

"""# Community Detection"""

from networkx.algorithms import community as nxcomm
kl_res = nxcomm.kernighan_lin_bisection(G)
print(kl_res)
print("Modularity",nxcomm.quality.modularity(G, communities = kl_res))

gmc_res = nxcomm.greedy_modularity_communities(G)
gmc_res

len(gmc_res)

nxcomm.quality.modularity(G, communities = gmc_res)

"""modularity is quite high. There exists a community structure."""

community_num_each_node = {}
for j in range(len(gmc_res)):
    list_to_iterate = list(gmc_res[j])
    for i in range(len(list_to_iterate)):
        key = list_to_iterate[i]
        if key not in community_num_each_node:
            community_num_each_node[key] = j

number_of_communities = pd.DataFrame([community_num_each_node]).T
number_of_communities =  number_of_communities.rename(columns={0:"number_of_communities"})
print(number_of_communities.shape)
print(cr.shape)
number_of_communities.head()

cr = cr.merge(number_of_communities,left_index=True, right_index=True)

plt.figure(figsize=(15,7))
p = sns.barplot(cr.number_of_communities.value_counts().index,cr.number_of_communities.value_counts().values)
plt.title("Size of the Communities")
plt.ylabel("Node Count")
plt.xlabel("Community ID")
p.set(xticklabels=[])
plt.show()

cr["size_community"] = cr.number_of_communities.map(dict(cr.number_of_communities.value_counts()))

cr.to_excel("cr.xlsx")

cr = pd.read_excel("cr.xlsx",index_col=0)
cr.head()

cr.describe().T

"""## Network Plot"""

plt.rcParams['figure.figsize'] = [30, 15]
pos = nx.spring_layout(G, seed = 1)
nx.draw_networkx_nodes(G, pos, node_color='b',node_size=30)
nx.draw_networkx_edges(G, pos, edgelist=G.edges(),width=0.8)
nx.draw_networkx_labels(G, pos, font_family="sans-serif",font_size =0)
ax = plt.gca()
plt.axis("off")
plt.show()

G1 = nx.from_pandas_edgelist(pd.read_csv('musae_facebook_edges.csv', header=0, names = ['source', 'target']), create_using=nx.Graph())
df2 = df.copy()
df2.page_type = df2.page_type.map({"tvshow":1,"government":2,"company":3,"politician":4})
lt1 = list(df2[df2.page_type == 1 ].index)
lt2 = list(df2[df2.page_type == 2 ].index)
lt3 = list(df2[df2.page_type == 3 ].index)
lt4 = list(df2[df2.page_type == 4 ].index)
node_attributes2 = df2.set_index('id').transpose().to_dict()
node_attributes2 = df2.set_index('id').transpose().to_dict()
nx.set_node_attributes(G1, node_attributes2)
G1.nodes(data=True)

plt.rcParams['figure.figsize'] = [60, 30]

nx.draw(G1, pos, edge_color='k',  with_labels=False,
         font_weight='light', node_size= 5, width= 0.8)

#For each community list, draw the nodes, giving it a specific color.
nx.draw_networkx_nodes(G1, pos, nodelist=lt1, node_color='g',alpha=0.8) # tvshow
nx.draw_networkx_nodes(G1, pos, nodelist=lt2, node_color='orange',alpha=0.8) # government
nx.draw_networkx_nodes(G1, pos, nodelist=lt3, node_color='b',alpha=0.8) # company
nx.draw_networkx_nodes(G1, pos, nodelist=lt4, node_color='r',alpha=0.8) # politician
plt.axis("off")
plt.show()

plt.rcParams['figure.figsize'] = [100, 50]

nx.draw(G1, pos, edge_color='k',  with_labels=False,
         font_weight='light', node_size= 5, width= 0.8)

nx.draw_networkx_nodes(G1, pos, nodelist=lt1, node_color='g',alpha=0.5)      # tvshow
nx.draw_networkx_nodes(G1, pos, nodelist=lt2, node_color='orange',alpha=0.5) # government
nx.draw_networkx_nodes(G1, pos, nodelist=lt3, node_color='b',alpha=0.5)      # company
nx.draw_networkx_nodes(G1, pos, nodelist=lt4, node_color='r',alpha=0.5)      # politician
plt.axis("off")
plt.title("green:tvshow , orange:government , blue:company , red:politician", fontsize=60)
plt.show()

"""# Helper Functions"""

# Ref: http://scikit-learn.org/stable/modules/learning_curve.html
def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=1, train_sizes=np.linspace(0.01, 1.0, 5),scoring="f1"):
    plt.figure(figsize=(10,6))
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes,scoring=scoring)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, '-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, '-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    plt.grid("on")
    return plt

def ROC_plotter(y_train_,y_test_,X_train_,X_test_,estimator):
    plt.figure(figsize=(14,4))
    plt.subplot(121)
    fpr, tpr, tresholds = met.roc_curve(y_train_ , estimator.predict_proba(X_train_)[:,1])
    roc_auc = met.roc_auc_score(y_train_ , estimator.predict_proba(X_train_)[:,1])
    plt.plot(fpr, tpr, label='ROC-AUC = %0.2f' % roc_auc, color='darkorange', linestyle='dashdot', lw=2)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Train ')
    plt.legend(loc="lower right")
    plt.subplot(122)
    fpr, tpr, tresholds = met.roc_curve(y_test_ , estimator.predict_proba(X_test_)[:,1] )
    roc_auc = met.roc_auc_score(y_test_ , estimator.predict_proba(X_test_)[:,1])
    plt.plot(fpr, tpr, label='ROC-AUC = %0.2f' % roc_auc, color='darkorange', linestyle='dashdot', lw=2)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Test')
    plt.legend(loc="lower right")
    plt.show()

def PrecisionRecallCurve(y_train_,y_test_,X_train_,X_test_,estimator):
    plt.figure(figsize=(14,4))
    plt.subplot(121)
    plt.title("Precision vs Recall Training")
    precision, recall, tresholds = met.precision_recall_curve(y_train_,estimator.predict_proba(X_train_)[:,1])
    plt.plot(tresholds,precision[:-1],"--",color="navy",label="Precison: TP / (TP+FP)")
    plt.plot(tresholds,recall[:-1],"--",color="darkorange",label='Recall: TP / (TP+FN)')
    plt.legend()
    plt.subplot(122)
    plt.title("Precision vs Recall Test")
    precision, recall, tresholds = met.precision_recall_curve(y_test_,estimator.predict_proba(X_test_)[:,1])
    plt.plot(tresholds,precision[:-1],"--",color="navy",label="Precison: TP / (TP+FP)")
    plt.plot(tresholds,recall[:-1],"--",color="darkorange",label='Recall: TP / (TP+FN)')
    plt.legend()
    plt.show()
    
def PrecisionRecallCurve2(y_train_,y_test_,X_train_,X_test_,estimator):
    plt.figure(figsize=(14,4))
    plt.subplot(121)
    plt.title("Precision vs Recall Training")
    precision, recall, tresholds = met.precision_recall_curve(y_train_,estimator.predict_proba(X_train_)[:,1])
    pr_auc = met.auc(recall, precision)
    plt.plot(recall,precision,"--",color="darkorange",label='LR (PR-AUC = %0.2f)' % pr_auc)
    no_skill = len(y_train_[y_train_==1]) / len(y_train_)
    plt.plot([0, 1], [no_skill, no_skill], linestyle='--', color='navy', label='No Skill')
    plt.legend()
    plt.xlabel("precision")
    plt.ylabel("recall")
    plt.title("precision recall curve")
    plt.subplot(122)
    plt.title("Precision vs Recall Test")
    precision, recall, tresholds = met.precision_recall_curve(y_test_,estimator.predict_proba(X_test_)[:,1])
    pr_auc = met.auc(recall, precision)
    plt.plot(recall,precision,"--",color="darkorange",label='LR (PR-AUC = %0.2f)' % pr_auc)
    no_skill = len(y_test[y_test==1]) / len(y_test)
    plt.plot([0, 1], [no_skill, no_skill], linestyle='--', color='navy', label='No Skill')
    plt.legend()
    plt.xlabel("precision")
    plt.ylabel("recall")
    plt.show()

"""# Modelling with Hand Engineered Features"""

modelling_data = cr.merge(df, left_index=True,right_index=True).drop(columns=["id"])

modelling_data.head(2)

correlation_matrix = modelling_data.corr()
plt.figure(figsize=(13,13))
ax = sns.heatmap(correlation_matrix, vmax=1, cbar=True, square=True, annot=True, fmt='.2f', 
                 annot_kws={'size': 12}, cmap='coolwarm')
ax.xaxis.set_ticks_position('top')
plt.yticks(rotation=0)
plt.xticks(rotation=90)
plt.show()

X = modelling_data.iloc[:,:-1]
y = modelling_data.iloc[:,-1]

num_list = list(X.columns)
num_list

num_list.remove("number_of_communities")
num_list

pipe_categoric = pip.Pipeline([
                                ("ohe",pre.OneHotEncoder(handle_unknown="ignore", sparse=False,))
                              ])
pipe_numeric = pip.Pipeline([
                                ("scaler", pre.StandardScaler())
                             ])

ct = com.ColumnTransformer([
              ("num", pipe_numeric, num_list),
              ("cat", pipe_categoric, ["number_of_communities"]), # This columns includes community Id. It needs to be one hot encoded
],remainder="passthrough")

pipe_tsne = pip.Pipeline([
              ("ct", ct),
              ("tsne", man.TSNE(n_components=2))
])
X_tsne = pipe_tsne.fit_transform(X)

plt.figure(figsize=(12,7))
sns.scatterplot(x=X_tsne[:, 0], y=X_tsne[:,1], hue=y)
plt.show()

"""It seems we will need more complex features. I will use PCA and check if there is any improvement """

def plot_component_cumulative_importance(pipe_pca, stepName):
  ratios = pipe_pca.named_steps[stepName].explained_variance_ratio_

  x_values = []
  y_values = []

  total = 0
  for i in range(0, len(ratios)):
    x_values.append(i+1)
    total += ratios[i]
    y_values.append(total)
  plt.figure(figsize=(15,7))
  plt.plot(x_values, y_values)
  plt.xlabel("Feature Number")
  plt.ylabel("Explained Variance")
  plt.grid(True)
  plt.show()

pipe_pca = pip.Pipeline([
            ("ct", ct),
            ("pca", dec.PCA()),
            
])
pipe_pca.fit(X)
plot_component_cumulative_importance(pipe_pca, "pca")

"""20 features seems okay for PCA to avoid unnecessary complexity of features"""

pipe_pca_tsne = pip.Pipeline([
              ("ct", ct),
              ("pca", dec.PCA(n_components=20)),
              ("tsne", man.TSNE(n_components=2))
])
X_tsne = pipe_pca_tsne.fit_transform(X)
plt.figure(figsize=(12,7))
sns.scatterplot(x=X_tsne[:, 0], y=X_tsne[:,1], hue=y)
plt.show()

X_train, X_test, y_train, y_test = mod.train_test_split(X, y, test_size=0.2, random_state=42, stratify = y)

# Logistic Regression without PCA

pipeline = pip.Pipeline( steps = [("ct", ct),
                                  #("pca", dec.PCA(n_components=20)),
                                  ('clf', lin.LogisticRegression(random_state=42))
                             ])
params_lr = [  {'clf__C'      : np.arange(0.1, 1, 0.1),
               'clf__penalty': ['l1'], 
               'clf__solver' : ['liblinear']},
               {'clf__C'      : np.arange(0.1, 1, 0.1), 
               'clf__penalty': ['l2'], 
               'clf__solver' : ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']}  
              ] 
#Kfold Stratified
kfold = mod.StratifiedKFold(n_splits=3)
grid = mod.GridSearchCV(estimator = pipeline, param_grid = params_lr, cv = kfold,verbose=1, n_jobs = -1)
grid.fit(X_train,y_train)
print('Grid accuracy on training data:', grid.score(X_train, y_train))
print('Grid accuracy on test data:', grid.score(X_test, y_test))
print("train")
print(met.classification_report(y_train, grid.predict(X_train)))
print("test")
print(met.classification_report(y_test, grid.predict(X_test)))

# Logistic Regression with PCA

pipeline = pip.Pipeline( steps = [("ct", ct),
                                  ("pca", dec.PCA(n_components=20)),
                                  ('clf', lin.LogisticRegression(random_state=42))
                             ])
params_lr = [  {'clf__C'      : np.arange(0.1, 1, 0.1),
               'clf__penalty': ['l1'], 
               'clf__solver' : ['liblinear']},
               {'clf__C'      : np.arange(0.1, 1, 0.1), 
               'clf__penalty': ['l2'], 
               'clf__solver' : ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']}  
              ] 
#Kfold Stratified
kfold = mod.StratifiedKFold(n_splits=3)
grid = mod.GridSearchCV(estimator = pipeline, param_grid = params_lr, cv = kfold,verbose=1, n_jobs = -1)
grid.fit(X_train,y_train)
print('Grid accuracy on training data:', grid.score(X_train, y_train))
print('Grid accuracy on test data:', grid.score(X_test, y_test))
print("train")
print(met.classification_report(y_train, grid.predict(X_train)))
print("test")
print(met.classification_report(y_test, grid.predict(X_test)))

"""PCA did not bring any further improvement on sparse training data. We will try a tree based algorithm."""

# Random Forest without PCA

pipeline = pip.Pipeline(steps=[ ("ct", ct),
                                ('clf', ens.RandomForestClassifier(random_state=42))
                              ])
params = {
    'clf__criterion': ['entropy', 'gini'],
    'clf__max_features': [6,8,10],
    'clf__max_depth': [6, 8,10],
    'clf__min_samples_leaf': [1, 2],
    'clf__min_samples_split': [2, 3],
    'clf__class_weight':[ "balance_subsample","balanced",None]}

kfold = mod.StratifiedKFold(n_splits=3)
grid  = mod.GridSearchCV(estimator=pipeline, param_grid=params, cv=kfold, scoring=met.make_scorer(met.f1_score, average='weighted'),verbose=1,n_jobs=-1)
grid.fit(X_train,y_train)
print(); print("Best CV score: %f using %s\n" % (grid.best_score_, grid.best_params_))
print('Grid accuracy on training data:', grid.score(X_train, y_train))
print('Grid accuracy on test data:', grid.score(X_test, y_test))
print("Training")
print(met.classification_report(y_train, grid.predict(X_train)))
print("Test")
print(met.classification_report(y_test, grid.predict(X_test)))

importances = grid.best_estimator_.named_steps["clf"].feature_importances_
std = np.std([grid.best_estimator_.named_steps["clf"].feature_importances_ for tree in  grid.best_estimator_.named_steps["clf"].estimators_], axis=0)
indices = np.argsort(importances)[::-1]
feature_names = X_train.columns.tolist()
# Print the feature ranking
print("Feature ranking:")
feature_list = []
for f in range(11):
#    print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))
    feature_list.append(feature_names[indices[f]])
    print("%2d. %15s %2d (%f)" % (f + 1, feature_names[indices[f]], indices[f], importances[indices[f]]))

# Random Forest with PCA

pipeline = pip.Pipeline(steps=[ ("ct", ct),
                                ("pca", dec.PCA(n_components=20)),
                                ('clf', ens.RandomForestClassifier(random_state=42))
                              ])
params = {
    'clf__criterion': ['entropy', 'gini'],
    'clf__max_features': [4,6,8],
    'clf__max_depth': [6, 8,10],
    'clf__min_samples_leaf': [1, 2],
    'clf__min_samples_split': [2, 3],
    'clf__class_weight':[ "balance_subsample","balanced",None]}

kfold = mod.StratifiedKFold(n_splits=3)
grid  = mod.GridSearchCV(estimator=pipeline, param_grid=params, cv=kfold, scoring=met.make_scorer(met.f1_score, average='weighted'),verbose=1,n_jobs=-1)
grid.fit(X_train,y_train)
print(); print("Best CV score: %f using %s\n" % (grid.best_score_, grid.best_params_))
print('Grid accuracy on training data:', grid.score(X_train, y_train))
print('Grid accuracy on test data:', grid.score(X_test, y_test))
print("Training")
print(met.classification_report(y_train, grid.predict(X_train)))
print("Test")
print(met.classification_report(y_test, grid.predict(X_test)))

"""PCA improved the results.

"""

title = 'Learning Curves for RF'
kfold = mod.StratifiedKFold(n_splits=2, shuffle=True, random_state=42)
plot_learning_curve(grid.best_estimator_, title, X_train, y_train, cv=kfold,scoring=met.make_scorer(met.f1_score, average='weighted'))
plt.show()

"""Results can be improved

# Representation Learning
"""

# Automated Node2Vec

"""Node2vec Grid Strategy:

    - Handmaid features' performance is not bad.Therefore, we will choose dimension parameters' values less than default (128) to not making the model too complex.
    - 64 is half of default and 16 is for the efficiency in run time. 
    - 80 is default and 40 is half of the default.
    - combinations of p and q values cover both DFS and BFS.
    - There are 36 different combinations of the parameters. We will save all to files to make node2vec features reusable. Based on trials above, using the 36 different feature file, we will a narrowed RandomForest Grid. 
    - We aim to maximize weighted F1 score to maximize precision and recall for all classes
    - We aim (minimum)  0.85 weighted F1
    - If we cannot get these result, we will keep tuning the node2vec features.
"""

parameters = {
                "dimensions":[16,64],
                "walk_length":[40,80],
                "p":[0.5,1,2],
                "q":[0.5,1,2] 
             }

hand_maid = num_list + ["number_of_communities"]

t = 4 
file_name = []
grid_name = []
t_list    = []

for i in range(len(parameters["dimensions"])):
    for j in range(len(parameters["walk_length"])):
        for k in range(len(parameters["p"])):
            for l in  range(len(parameters["q"])):
                grid_string = "d_"+str(parameters["dimensions"][i]) + "_w_" +str(parameters["walk_length"][j]) + "_p_"+str(parameters["p"][k])+"_q_"+str(parameters["q"][l])
                print(grid_string)
                file_string = "embs" + str(t) + ".txt"
                n2v = Node2Vec(G, dimensions=parameters["dimensions"][i], walk_length=parameters["walk_length"][j], num_walks=10, p = parameters["p"][k], q = parameters["q"][l], workers=4, seed=42) 
                model = n2v.fit(window=10)                
                model.wv.save_word2vec_format(file_string)
                print("saved_"+file_string)
                t_list.append(t)
                file_name.append(file_string)
                grid_name.append(grid_string)
                t += 1

grid_map = pd.DataFrame({"t":t_list,"file_name":file_name,"grid_name":grid_name})
grid_map

hand_maid = num_list + ["number_of_communities"]
t = 4
train_f1   =  []
test_f1    =  []
file_names =  []
t_list_    =  []

"""
Pipe steps:
    1-Hand-Engineered features
        -All hand-enginered features are numeric but number of communities. Number of Communities includes community ID of the node
        -Number of Community will be one hot encoded
        -Rest of the hand engineered features will be scaled for PCA
        -Combination of Numeric and One-Hot Encoded features are sparse (too unnecessary complexity). In addition, there are highly correlated features.
        -In order to avoid sparsity, complexity and high correlation, PCA will be used.
        -20 features created by PCA includes app. %98 of the explained variance.
        -First column transformer helps us to create sparse onehot encoded and scaled hand-engineered feature matrix
        -Second column transformer helps us to create 20 hand engineed features via PCA
        -First column transformer is the first step of the hand maid feature pipeline and hand maid feature pipeline is the first sted of the second column transformer.
        
    2-By using nested pipelines mentioned above, node2vec embedding vectors and hand enginered features from the train set are combined. 
  
"""
pipe_categoric = pip.Pipeline([
                                ("ohe",pre.OneHotEncoder(handle_unknown="ignore", sparse=False))
                              ])
pipe_numeric = pip.Pipeline([
                                ("scaler", pre.StandardScaler()),
                             ])

ct = com.ColumnTransformer([
                           ("num", pipe_numeric, num_list),
                           ("cat", pipe_categoric, ["number_of_communities"]), # This columns includes community Id. It needs to be one hot encoded
                           ],remainder="passthrough")

pipeline_hand_maid = pip.Pipeline([ 
                                  ("ct", ct),
                                  ("pca", dec.PCA(n_components=20)),
                                  ])

ct2 = com.ColumnTransformer([
                           ("handmaid", pipeline_hand_maid, hand_maid)],
                            remainder="passthrough")

pipeline = pip.Pipeline([ 
                        ("ct2", ct2),
                        ('clf', ens.RandomForestClassifier(random_state=42))
                        ])

params = {
            'clf__criterion': ['gini'],
            'clf__max_features': [6,8,10],
            'clf__max_depth': [6,8,10],
            'clf__min_samples_leaf': [1],
            'clf__min_samples_split': [3],
            'clf__class_weight':["balanced"]}

kfold = mod.StratifiedKFold(n_splits=3)
grid  = mod.GridSearchCV(estimator=pipeline, param_grid=params, cv=kfold, scoring=met.make_scorer(met.f1_score, average='weighted'),verbose=1,n_jobs=-1)

for i in range(4,40):
    file_string = "embs" + str(t) + ".txt"
    print(file_string)
    embs = pd.read_csv(file_string, sep=' ', skiprows=1, header=None, index_col = 0)
    modelling_data_emb = embs.merge(modelling_data,right_index=True, left_index=True)
    X = modelling_data_emb.iloc[:,:-1]
    y = modelling_data_emb.iloc[:,-1]
    X_train, X_test, y_train, y_test = mod.train_test_split(X, y, test_size=0.2, random_state=42, stratify = y)
    file_names.append(file_string)

    grid.fit(X_train,y_train)
     
    print("Best CV score: %f using %s\n" % (grid.best_score_, grid.best_params_))
    print('Grid accuracy on training data:', grid.score(X_train, y_train))
    print('Grid accuracy on test data:', grid.score(X_test, y_test))
    print("test f1",met.f1_score(y_test, grid.predict(X_test), average='weighted'))
    print("train f1",met.f1_score(y_train, grid.predict(X_train), average='weighted'))
    train_f1.append(met.f1_score(y_train, grid.predict(X_train), average='weighted'))
    test_f1.append(met.f1_score(y_test, grid.predict(X_test), average='weighted'))
    t_list_.append(t)
    t += 1
    print("="*50)

grid_map2 = pd.DataFrame({"file_name":file_names,"t":t_list_,"train_weighted_f1":train_f1,"test_weighted_f1":test_f1}).merge(grid_map.grid_name,left_index=True,right_index=True).sort_values(by="test_weighted_f1",ascending=False)
grid_map2

grid_map2.to_excel("grid_results.xlsx")

plt.figure(figsize=(12,7))
plt.plot(grid_map2.grid_name,grid_map2.test_weighted_f1,color="r",lw=2)
plt.xticks(grid_map2.grid_name, grid_map2.grid_name, rotation='vertical')
plt.xlabel("node2vec parameter combination")
plt.ylabel("Weighted F1 score of Test Data")
plt.title("d:dimension , w:walk lenght, p:p , q:q")
plt.show()

"""Best node2vec parameter combination is : embs16

    -Dimension:16
    -Walk lenght : 80
    -p=1
    -q=0.5
    -number of walks = 10
    
Best CV score: 0.908368 using the following RF Grid 

    -clf__class_weight': 'balanced'
    -clf__criterion': 'gini'
    -clf__max_depth': 10
    -clf__max_features': 10
    -clf__min_samples_leaf': 1
    -clf__min_samples_split': 3

    -Grid accuracy on training data: 0.958431421320217
    -Grid accuracy on test data: 0.9109995106063957
    -test f1 0.9109995106063957
    -train f1 0.958431421320217

# Feature Importances
"""

embs = pd.read_csv("embs16.txt", sep=' ', skiprows=1, header=None, index_col = 0)
modelling_data_emb = embs.merge(modelling_data,right_index=True, left_index=True)
X = modelling_data_emb.iloc[:,:-1]
y = modelling_data_emb.iloc[:,-1]
X_train, X_test, y_train, y_test = mod.train_test_split(X, y, test_size=0.2, random_state=42, stratify = y)
modelling_data_emb.head(2)

pipe_categoric = pip.Pipeline([
                                ("ohe",pre.OneHotEncoder(handle_unknown="ignore", sparse=False))
                              ])
pipe_numeric = pip.Pipeline([
                                ("scaler", pre.StandardScaler()),
                             ])

ct = com.ColumnTransformer([
                           ("num", pipe_numeric, num_list),
                           ("cat", pipe_categoric, ["number_of_communities"]), # This columns includes community Id. It needs to be one hot encoded
                           ],remainder="passthrough")

pipeline_hand_maid = pip.Pipeline([ 
                                  ("ct", ct),
                                  ("pca", dec.PCA(n_components=20)),
                                  ])

ct2 = com.ColumnTransformer([
                           ("handmaid", pipeline_hand_maid, hand_maid)],
                            remainder="passthrough")

pipeline = pip.Pipeline([ 
                        ("ct2", ct2),
                        ('clf', ens.RandomForestClassifier(random_state=42))
                        ])

params = {
            'clf__criterion': ['gini'],
            'clf__max_features': [10],
            'clf__max_depth': [10],
            'clf__min_samples_leaf': [1],
            'clf__min_samples_split': [3],
            'clf__class_weight':["balanced"]}

kfold = mod.StratifiedKFold(n_splits=3)
grid  = mod.GridSearchCV(estimator=pipeline, param_grid=params, cv=kfold, scoring=met.make_scorer(met.f1_score, average='weighted'),verbose=1,n_jobs=-1)
grid.fit(X_train,y_train)

print(); print("Best CV score: %f using %s\n" % (grid.best_score_, grid.best_params_))
print('Grid accuracy on training data:', grid.score(X_train, y_train))
print('Grid accuracy on test data:', grid.score(X_test, y_test))
print("test f1",met.f1_score(y_test, grid.predict(X_test), average='weighted'))
print("train f1",met.f1_score(y_train, grid.predict(X_train), average='weighted'))

print(met.classification_report(y_test,grid.predict(X_test)))

x_train_features = pipeline[0].fit_transform(X_train)
x_train_features= pd.DataFrame(x_train_features)

importances = grid.best_estimator_.named_steps["clf"].feature_importances_
std = np.std([grid.best_estimator_.named_steps["clf"].feature_importances_ for tree in  grid.best_estimator_.named_steps["clf"].estimators_], axis=0)
indices = np.argsort(importances)[::-1]
feature_names = x_train_features.columns.tolist()
# Print the feature ranking
print("Feature ranking:")
feature_list = []
for f in range(x_train_features.shape[1]):
    feature_list.append(feature_names[indices[f]])
    print("%2d. %15s %2d (%f)" % (f + 1, feature_names[indices[f]], indices[f], importances[indices[f]]))
# Plot the feature importances of the forest
plt.figure(figsize=(15,6))
plt.title("Feature importances")
plt.bar(range(x_train_features.shape[1]), importances[indices],
       color="r", yerr=std[indices], align="center")
plt.xticks(range(x_train_features.shape[1]), feature_list, rotation='vertical')
#plt.xlim([-1, x_train_features.shape[1]])
plt.show()

"""Indexes bw 0-19 are hand engineered features:
   
Source:Documentation of ColumnTransformer:
Notes

The order of the columns in the transformed feature matrix follows the order of how the columns are specified in the transformers list. Columns of the original feature matrix that are not specified are dropped from the resulting transformed feature matrix, unless specified in the passthrough keyword. Those columns specified with passthrough are added at the right to the output of the transformers.
https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html#sklearn.compose.ColumnTransformer.get_feature_names
"""

correlation_matrix = x_train_features.corr()
plt.figure(figsize=(20,10))
ax = sns.heatmap(correlation_matrix, vmax=1, cbar=True, square=True, annot=False, fmt='.2f', 
                 cmap='coolwarm')
ax.xaxis.set_ticks_position('top')
plt.yticks(rotation=0)
plt.xticks(rotation=90)
plt.show()

"""# TSNE Visualization of the feature set"""

pipe_pca_tsne = pip.Pipeline([ 
                        ("ct2", ct2),
                        ("tsne", man.TSNE(n_components=2))
                        ])
X_tsne = pipe_pca_tsne.fit_transform(X)
plt.figure(figsize=(12,7))
sns.scatterplot(x=X_tsne[:, 0], y=X_tsne[:,1], hue=y)
plt.show()

"""# Performance of the hand enginered features"""

embs = pd.read_csv("embs16.txt", sep=' ', skiprows=1, header=None, index_col = 0)
modelling_data_emb = embs.merge(modelling_data,right_index=True, left_index=True).drop(columns=hand_maid,axis=1)
modelling_data_emb.head(2)

X = modelling_data_emb.iloc[:,:-1]
y = modelling_data_emb.iloc[:,-1]
X_train, X_test, y_train, y_test = mod.train_test_split(X, y, test_size=0.2, random_state=42, stratify = y)

pipeline = pip.Pipeline(steps=[ 
                                ('clf', ens.RandomForestClassifier(random_state=42))
                              ])
params = {
    'clf__criterion':    ['gini'],
    'clf__max_features': [10],
    'clf__max_depth':    [10],
    'clf__min_samples_leaf':  [1],
    'clf__min_samples_split': [3],
    'clf__class_weight':[ "balanced"]}

kfold = mod.StratifiedKFold(n_splits=3)
grid  = mod.GridSearchCV(estimator=pipeline, param_grid=params, cv=kfold, scoring=met.make_scorer(met.f1_score, average='weighted'),verbose=1,n_jobs=-1)
grid.fit(X_train,y_train)

print(); print("Best CV score: %f using %s\n" % (grid.best_score_, grid.best_params_))
print('Grid accuracy on training data:', grid.score(X_train, y_train))
print('Grid accuracy on test data:', grid.score(X_test, y_test))
print(met.classification_report(y_test,grid.predict(X_test)))
print("test f1",met.f1_score(y_test, grid.predict(X_test), average='weighted'))
print("train f1",met.f1_score(y_train, grid.predict(X_train), average='weighted'))

"""Hand enginered features improved model performance from 0.909 to 0.911


"""