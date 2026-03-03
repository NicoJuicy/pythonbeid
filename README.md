
# PythonBEID

PythonBEID est un module Python pour lire les informations essentielles des cartes d'identité belge à l'aide d'un lecteur de cartes PC/SC et de la bibliothèque `pyscard`.

## Installation

```bash
pip install pythonbeid
```

## Utilisation

```python
from pythonbeid import CardReader, NoReaderError, NoCardError

try:
    with CardReader() as cr:          # context manager — ferme proprement la connexion
        info = cr.read_informations(photo=False)
        print(info["last_name"])      # Smith
        print(info["birth_date"])     # datetime(1990, 1, 1)
except NoReaderError:
    print("Aucun lecteur de carte détecté.")
except NoCardError:
    print("Aucune carte dans le lecteur.")
```

Si plusieurs lecteurs sont connectés, précisez l'index :

```python
with CardReader(reader_index=1) as cr:
    info = cr.read_informations()
```

### Champs retournés par `read_informations()`

| Clé | Type | Description |
|---|---|---|
| `card_number` | str | Numéro de la carte |
| `validity_start` | datetime | Date début de validité |
| `validity_end` | datetime | Date fin de validité |
| `issuing_municipality` | str | Commune de délivrance |
| `national_number` | str | Numéro national |
| `last_name` | str | Nom de famille |
| `first_names` | str | Prénom(s) |
| `suffix` | str | Suffixe de nom |
| `nationality` | str | Nationalité |
| `birth_place` | str | Lieu de naissance |
| `birth_date` | datetime | Date de naissance |
| `sex` | str | Sexe |
| `address` | str | Adresse |
| `postal_code` | str | Code postal |
| `city` | str | Localité |
| `photo` | str | Photo en base64 (si `photo=True`) |

### Activer les logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dépendances

- `pyscard`

## Tests

```bash
pip install -e ".[dev]"
pytest                          # tous les tests (matériel skippé si absent)
pytest tests/test_parser.py     # tests sans matériel uniquement
```

## Contribuer

Les contributions et améliorations sont les bienvenues !

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
