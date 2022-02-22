# Inferencia gramatical de lenguajes incontextuales mediante computación natural y evolutiva

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
