# Shopping Cart Knapsack Problem with Quantity Discounts and Category Constraints - Discrete Knapsack Variant for Shopping Cart Optimization

### Projekt dotyczy optymalizacji koszyka zakupowego przy użyciu Artificial Bee Colony, potraktowanego jako wariant problemu plecakowego.

Zamiast klasycznego plecaka:

- przedmioty to produkty sklepowe,

- ograniczenia dotyczą:
  - objętości koszyka,

  - opcjonalnie budżetu,

- część produktów ma promocje ilościowe z limitem produktów,

- część produktów nie ma promocji,

- dodatkowo istnieje lista zakupów na poziomie kategorii, np.:
  - trzeba kupić owoce,

  - trzeba kupić nabiał,

  - trzeba kupić pieczywo.

#### Cel

Zmaksymalizować zaoszczędzoną kwotę na promocjach, przy jednoczesnym spełnieniu ograniczeń.

Oszczędność liczona jest jako różnica:

- kosztu wszystkich wybranych produktów po cenach standardowych

- rzeczywistego kosztu po uwzględnieniu promocji.

#### Założenia problemu

**Produkty**

Każdy produkt ma:

- nazwę,

- kategorię,

- cenę standardową,

- objętość jednostkową,

- informację, czy ma promocję (część produktów nie jest promocyjna),

- typ promocji, jeśli ją ma.

Przykładowe kategorie:

- owoce,

- warzywa,

- nabiał,

- pieczywo,

- napoje.

**Promocje ilościowe**

Promocje posiadają limit sztuk będący podwojoną minimalną liczbą produktów koniecznych do spełnienia promocji.

Przykładowe promocje:

- 1+1 gratis (limit 4 sztuki),

- 2+1 gratis (limit 6 sztuk),

- 2+2 gratis (limit 8 sztuk),

- 3+1 gratis (limit 8 sztuk).

Limit ten odnosi się do maksymalnej liczby sztuk, dla których promocja może zostać naliczona. Zakup powyżej tego limitu jest możliwy, ale w cenie standardowej.

**Lista zakupów**

Dla każdej pozycji listy zakupów określona jest:

- kategoria,

- wymagane minimum sztuk,

- informacja, czy produkty muszą być różne.

Przykładowe pozycje na liście zakupów:

- owoce: minimum 2, różne = True,

- nabiał minimum 2, różne = False,

- pieczywo: minimum 1, różne = False.

**Ograniczenia zakupów**

- objętość koszyka,

- lista zakupów,

- w zależności od wariantu:
  - wariant budżetowy "przed wypłatą" - ograniczenie budżetu

  - wariant bez budżetu "po wypłacie" - brak ograniczenia budżetu
