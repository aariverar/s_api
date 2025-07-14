Feature: Automatizacion de Servicios

  @Santander
  Scenario Outline: Api Test "<datos>"
    Given se extrae los datos del servicio del excel "<datos>"
    When cuando envio una peticion al servicio "<datos>"
    Then se valida el status code obtenido con el status code esperado "<datos>"
    And se valida la estructura del response obtenido con el response esperado "<datos>"
    And se valida el response obtenido con el response esperado "<datos>"
    And se valida los headers del response obtenido con los headers esperados "<datos>"

    Examples:
      | datos |
      |     1 |
      |     2 |
      |     3 |
      |     4 |
      |     5 |
      |     6 |
      |     7 |
      |     8 |
      |     9 |
      |    10 |