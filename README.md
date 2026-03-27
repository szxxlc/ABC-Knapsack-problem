# Shopping Cart Knapsack Problem with Quantity Discounts and Category Constraints - Discrete Knapsack Variant for Shopping Cart Optimization

### Projekt dotyczy optymalizacji koszyka zakupowego przy użyciu Artificial Bee Colony, potraktowanego jako wariant problemu plecakowego.

Zamiast klasycznego plecaka:

- przedmioty to produkty sklepowe,

- ograniczenia dotyczą:
  - objętości koszyka,

  - opcjonalnie budżetu,

- część produktów ma promocje ilościowe z limitem liczby sztuk objętych promocją,

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

- informacja, czy produkty muszą być różne,

- kara za każdą brakującą jednostkę wymagania.

Przykładowe pozycje na liście zakupów:

- owoce: minimum 2, różne = True, kara = 3.0,

- nabiał minimum 2, różne = False, kara = 1.5,

- pieczywo: minimum 1, różne = False. kara = 2.0,

**Ograniczenia zakupów**

- objętość koszyka,

- lista zakupów,

- w zależności od wariantu:
  - wariant budżetowy "przed wypłatą" - ograniczenie budżetu

  - wariant bez budżetu "po wypłacie" - brak ograniczenia budżetu

Objętość koszyka oraz budżet są ograniczeniami **twardymi**.  
Lista zakupów jest ograniczeniem **miękkim** - jej niespełnienie nie odrzuca rozwiązania, lecz powoduje naliczenie kary proporcjonalnej do stopnia niespełnienia wymagań.

---

### Reprezentacja rozwiązania

Dla każdego produktu $i$ zmienna decyzyjna ma postać:

$x_i \in \{0, 1, 2, \ldots\}$

gdzie $x_i$ oznacza liczbę kupionych sztuk produktu $i$.

Całe rozwiązanie można więc zapisać jako wektor:

$x = (x_1, x_2, \ldots, x_n)$

Produkt $i$ ma:

- cenę jednostkową $p_i$,

- objętość jenostkową $v_i$,

- kategorię $c_i$,

- opcjonalną promocję typu $a_i + b_i$ gratis,

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

$ F(x)=\max{savings(x)-penalty_c(x)} = \max{regularCost(x) - actualCost(x) - penalty_c(x)}$

#### Koszt regularny

Koszt regularny wszystkich produktów w koszyku:

$regularCost(x) = \sum_{i=1}^{n} p_i x_i$

#### Koszt rzeczywisty

Koszt rzeczywisty po uwzględnieniu promocji:

$actualCost(x) = \sum_{i=1}^{n} actualCost_i(x_i)$

#### Oszczędność

Oszczędność definiowana jest jako różnica między kosztem regularnym a rzeczywistym:

$savings(x) = regularCost(x) - actualCost(x)$

#### Niedobór dla wymagania kategorii

Dla kategorii $c$ oraz przypisanego minimum $R_c$ definiowany jest niedobór.

Jeśli dla danej kategorii $different = False$:

$shortage_c(x) = \max\left(0, R_c - \sum_{i \in I_c} x_i\right)$

Jeśli dla danej kategorii $different = True$:

$shortage_c(x) = \max\left(0, R_c - \sum_{i \in I_c} \mathbf{1}(x_i > 0)\right)$

#### Kara za wymaganie kategorii

Dla każdej kategorii definiowana jest kara jednostkowa $\lambda_c$ za każdą brakującą jednostkę wymagania:

$penalty_c(x) = \lambda_c \cdot shortage_c(x)$

#### Łączna kara za listę zakupów

$shoppingPenalty(x) = \sum_{c \in C} penalty_c(x)$

#### Cel optymalizacji

Celem jest maksymalizacja wyniku rozwiązania:

$\max \ score(x)$

gdzie:

$score(x) = savings(x) - shoppingPenalty(x)$

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

#### Lista zakupów jako ograniczenie miękkie

Lista zakupów nie jest traktowana jako ograniczenie twarde.  
Jej niespełnienie powoduje naliczenie kary uwzględnianej w funkcji celu.

Dla kategorii $c$ kara zależy od niedoboru względem wymaganego minimum:

- dla wymagań bez różnorodności liczony jest brak łącznej liczby sztuk,
- dla wymagań z różnorodnością liczony jest brak liczby różnych produktów w kategorii.
