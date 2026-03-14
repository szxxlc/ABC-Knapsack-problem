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

---

### Reprezentacja rozwiązania

Dla każdego produktu $i$ zmienna decyzyjna ma postać:

$x_i \in \{0, 1, 2, \ldots\}$

gdzie $x_i$ oznacza liczbę kupionych sztuk produktu $i$.

Całe rozwiązanie można więc zapisać jako wektor:

$x = (x_1, x_2, \ldots, x_n)$

Produkt $i$ ma:

- cenę jednostkową $p_i$,

- promocję typu $a_i + b_i$ gratis,

- zakupioną liczbę sztuk $x_i$.

Dla każdego produktu promocyjnego limit promocyjny nie jest zadawany osobno - promocja może zostać naliczona maksymalnie dla dwóch pełnych pakietów promocyjnych:

$L_i = 2(a_i + b_i)$

Zakup dzielony jest na dwie części:

- **część objęta promocją**

  $y_i = \min(x_i, L_i)$

- **część nieobjęta promocją**

  $z_i = x_i - y_i$

Dla części promocyjnej:

- wielkość pakietu wynosi:

  $g_i = a_i + b_i$

- liczba pełnych pakietów:

  $k_i = \left\lfloor \dfrac{y_i}{g_i} \right\rfloor$

- reszta:

  $r_i = y_i \bmod g_i$

**Koszt części promocyjnej:**

$promoCost_i = k_i \cdot a_i \cdot p_i + r_i \cdot p_i$

**Koszt części niepromocyjnej:**

$extraCost_i = z_i \cdot p_i$

**Łączny rzeczywisty koszt produktu:**

$actualCost_i(x_i) = promoCost_i + extraCost_i$

**Dla produktu bez promocji:**

$actualCost_i(x_i) = x_i \cdot p_i$

### Funkcja celu

#### Koszt regularny

Koszt regularny wszystkich produktów w koszyku:

$regularCost(x) = \sum_{i=1}^{n} p_i x_i$

#### Koszt rzeczywisty

Koszt rzeczywisty po uwzględnieniu promocji:

$actualCost(x) = \sum_{i=1}^{n} actualCost_i(x_i)$

#### Oszczędność

Oszczędność definiowana jest jako różnica między kosztem regularnym a rzeczywistym:

$savings(x) = regularCost(x) - actualCost(x)$

#### Cel optymalizacji

Celem jest maksymalizacja oszczędności:

$\max \ savings(x)$

### Ograniczenia

#### Ograniczenie objętości

Niech:

$v_i$ oznacza objętość jednej sztuki produktu,

$V$ oznacza maksymalną pojemność koszyka.

Wówczas:

$\sum_{i=1}^{n} v_i x_i \leq V$

#### Ograniczenie budżetu

Występuje tylko w wariancie budżetowym „przed wypłatą”.

Niech:

$B$ oznacza dostępny budżet.

Wówczas:

$actualCost(x) \leq B$

#### Ograniczenia listy zakupów - bez wymogu różnorodności

Dla kategorii $c$:

$R_c$ — wymagane minimum,

$I_c$ — zbiór produktów należących do tej kategorii.

Jeśli dla danej kategorii $different = False$, to wymaganie ma postać:

$\sum_{i \in I_c} x_i \geq R_c$

Oznacza to, że liczy się łączna liczba sztuk produktów z tej kategorii.

#### Ograniczenia listy zakupów - z wymogiem różnorodności

Jeśli dla danej kategorii $different = True$, to trzeba kupić odpowiednią liczbę różnych produktów należących do tej kategorii.

W modelu matematycznym można wprowadzić pomocnicze zmienne binarne:

$u_i = \begin{cases} 1 & \text{jeśli } x_i > 0 \\ 0 & \text{jeśli } x_i = 0 \end{cases}$

Wtedy dla kategorii $c$:

$\sum_{i \in I_c} u_i \geq R_c$
