# Inferencia gramatical de lenguajes incontextuales mediante computación natural y evolutiva

## Libraries


## TODO

### Primera iteración
- [x] Generador de gramáticas en Forma normal de Chomsky
  - Dados:
    - Los símbolos terminales
    - Los símbolos no terminales
    - El número de producciones de la forma ```A → AB```
    - El número de producciones de la forma ```A → a```
  - Devuelve un string codificando la gramática generada 
- [x] Algortimo CYK para comprobar si una gramática genera una palabra
- [x] Función de fitness
  - Dada una cadena positiva x<sup>+</sup> y una gramática G
    - f(x<sup>+</sup>, G) = 1 SI CYK(x<sup>+</sup>, G)
    - f(x<sup>+</sup>, G) = d(x<sup>+</sup>, w) SINO (siendo w una palabra generada por G lo más cercana posible a x<sup>+</sup>)
  - Dada una cadena negativa x<sup>-</sup> y una gramática G
    - f(x<sup>-</sup>, G) = 0 SI CYK(x<sup>+</sup>, G)
    - f(x<sup>-</sup>, G) = 1 SINO
- [x] Generador de cadenas para los lenguajes de test

### Segunda iteración
- [ ] Función de fitness
  - La función anterior tenía un alto coste para las gramáticas que no pasaban el CYK, usaremos una versión alternativa del
    CYK para calcular el fitness en dicho caso.
    - Probaremos comprobando cual es la aparición de S más cercana al final de la tabla y usando la palabra que genere para
      evaluar, en el caso de que no aparezca, seguiremos usando fuerza bruta.
- [ ] La recombinación se dará con todas las gramáticas, pero tras ella se eliminarán las que tengan peor fitness.