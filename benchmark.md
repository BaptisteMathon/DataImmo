Lors de ce benchmark, nous allons comparer les performances de Pandas et Spark sur un traitement de données massif.

Pour ce faire, 2 tests ont été effectués. Ces 2 tests portent sur le calcul du prix moyen / m2. L'un sur 4 année (2021 à 2024), et un autre sur l'année 2023. L'idée étant de voir l'impact du nombre de lignes traitées sur les performances des deux technologies.

- Calcul du prix moyen / m2 sur 4 années (2021 à 2024) :

![alt text](<Img/BENCHMARK - 2021 - 2024.png>)

Comme nous pouvons voir sur cette capture l'utilisation de Spark (5.64 secondes) est beaucoup plus intérressante que Pandas (57.55 secondes)
Soit une différence de 51.91 secondes.

- Calcul du prix moyen / m2 sur 1 année (2023) :

![alt text](<Img/BENCHMARK - 2023.png>)

Sur une seule année la différence est beaucoup moins importe que sur 4 ans.
Cependant Spark (4.71 secondes) reste plus rapide que Pandas (11.64 secondes), avec une différence de 6.93 secondes.
