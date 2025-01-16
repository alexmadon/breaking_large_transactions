# breaking_large_transactions

Pour comprendre pourquoi casser un "large transaction" aide lors d'un FULL reindex Solr sur Alfresco, j'ai fait le petit test suivant:

1) je crée 100 folders dans "shared", dans une seule transaction. Cela est très simole à faire  : il suffit de faire un POST sur l'api

http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/nodes/-shared-/children

avec une liste (JSON) de folder. En effet cette api supporte les liste comme l'indique la documentation à :

https://docs.alfresco.com/content-services/latest/develop/rest-api-guide/#creating-multiple-entities-items

"Most POST endpoints that create entities actually allow an array of objects to be passed in the body, which creates each one individually, but within the same transaction."

Pour faire cet appel, tu peux utiliser le script python en attachemnt avec l'option '-c'
Puis tu sauvegardes l'état de la table alf_node avec:

```
psql -qAtX -c "with t1 as (select id,transaction_id,version from alf_node), t2 as (select transaction_id,count(transaction_id),json_agg(t1.*) from t1 group by transaction_id order by transaction_id) select json_agg(t2) FROM t2;" acs2332pgslr | jq > data_after_create_100nodes_in_on_transaction.json
```

2) je fais des "dummy" update sur les 100 folders créés en 1). Avec l'API REST, je ne peux pas faire des batches mais pour démontrer ce qui se passe, cette limitation n'est pas un problème : je fais un PUT sur les 100 folders, un par un (donc l'équivalent d'un bacth size de 1, pas le plus rapde, mais Ok pour la démonstration)

Pour faire cet appel, tu peux utiliser le script python en attachement avec l'option '-u'
Puis tu sauvegardes l'état de la table alf_node avec:

```
psql -qAtX -c "with t1 as (select id,transaction_id,version from alf_node), t2 as (select transaction_id,count(transaction_id),json_agg(t1.*) from t1 group by transaction_id order by transaction_id) select json_agg(t2) FROM t2;" acs2332pgslr | jq > data_after_updting_each_node_to_break_large_transaction-into_smaller.json

```


3) finalement, en utilisant ton programme favori de "diff", tu compares l'état avant l'update et après l'update :
(j'attache mes deux fichiers
```
data_after_create_100nodes_in_on_transaction.json
data_after_updting_each_node_to_break_large_transaction-into_smaller.json
```
)
tu vois que
a) avant l'update, tu as une grosse transaction pour les 100 noeuds, chaque noeud ayant la version 1.
b) après l'update, la transaction ID précédente a simplement disparu : le noeuds apparaissent avec une version 2 et une tout autre "transaction ID".
Ceci explique pourquoi lors d'un FULL reindex, Solr ne vois pas la vielle grosse transaction:
elle n'apparait plus dans la table alf_node.
