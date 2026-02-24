# Arquitectura Matemática del Motor Active Recall (Nexus)

Este documento destila la lógica algorítmica y el flujo de Experiencia de Usuario (UX) implementado en `modules/study_engine.py`. Sirve como manual de referencia para futuras mejoras o integraciones de modelos matemáticos más avanzados.

## 1. El Flujo de Sesión (El Pomodoro Interactivo)

El sistema de estudio está diseñado bajo una arquitectura de "Context-First" (Contexto Primero) para evitar la fragmentación cognitiva típica de las Flashcards aisladas. El bucle oficial es el siguiente:

1. **Obtención de la Pila (Due Cards):** 
   - La base de datos es sondeada buscando tarjetas donde `next_review` sea nulo (tarjetas nuevas no tocadas aún por ti) o donde `next_review <= now` (tarjetas vencidas que tu curva del olvido dictamina repasar hoy).
   - *Adelanto:* Existe el modo "Adelantar", el cual revoca el query de tiempo y escupe la pila entera para forzar repasos agendados en días futuros si la persona tiene energía sobrante.
   - *Filtrado Selectivo:* Se incluyó el `topic_id`. Esto inyecta un `.filter(Card.parent_id == topic_id)` al query inicial, permitiendo aislar el Pomodoro a las tarjetas de un único libro en lugar de estudiar materias aglomeradas.

2. **Renderizado Constante (La Cabecera):**
   - Para no saturar con saltos de consola ininteligibles (overlaps), se encapsuló un dibujador de cabeceras puras `draw_header()` que aplica una función `console.clear()` antes de redibujar métricas. Prometes visibilidad impecable del: 
     - **Reloj (Tiempo Sobrante):** Fuerte condicionante visual si baja de 5 minuros (cyan a `[bold white on red]`).
     - **Pila Actual:** El conteo iterativo (`enumerate`) de `[Tarjeta X de Y]`.
     - **Contexto Clickeable:** Panel explícito del `Tema de Estudio (Registry.title)`.

3. **La Demora Táctica y La Fuente 'f':**
   - El UX detiene agresivamente la impresión de la "Pregunta" para forzar al usuario a asimilar el tema. En la cabecera está la URL (`disp_url`). 
   - Se le da la posibilidad de apretar **'f'**. Esto invoca una bifurcación de subsistema operativo (`os.startfile` o web url en `webbrowser`) permitiéndote releer tu vieja nota de Notion o PDF antes de enfrentar la pregunta.

4. **El Relámpago Mental (Pregunta y Respuesta Sensorial):**
   - Se pinta el Panel Azul (`question`). Se detona un cronómetro milimétrico en Python (`action_start_time = time.time()`).
   - *Input Híbrido:* En el Prompt que frena tu consola, puedes escribir literalmente la respuesta desde el teclado físico (lo que retuerce mejor los caminos neuronales) o presionar Enter vacío si decidiste sólo pensar la respuesta mentalmente en una décima de segundo.
   - Si escribes la String oculta de emergencia `salir`, el Pomodoro rompe el Loop para regresarte a casa (`break`).

5. **El Contraste Final:**
   - La verdad (`answer`) baja en verde brillante. Si te aventuraste a teclear la tuya temporalmente, el sistema la imprimirá textualmente pegadita a la Original del Sistema (`Tú escribiste:` VS `Respuesta Correcta del Sistema:`).

---

## 2. El Cerebro Espaciado (El Algoritmo SM-2 Modificado)

Un motor de Active Recall no sirve de nada si las fechas para volver a repasar fallan. En Nexus utilizamos la clase matemática `SRSEngine` para evaluar la Puntuación del Usuario (Del 1 al 3). Así se ajustan los factores de retención:

### A. Evaluador de Dificultad (Difficulty 1.0 - 10.0)
Define qué tan "tóxicamente densa" es la pregunta semánticamente para tu cerebro.
- Al nacer la Tarjeta, se calcula su dificultad base invirtiendo las matemáticas de tu primer grado (1 Fácil -> Dificulta poco. 3 Difícil -> Dificulta grave).
- Con el tiempo, cada vez que repasas, el algoritmo amortigua un poco de esa dificultad natural aplicando la inercia:
  `card.difficulty = max(1.0, min(10.0, card.difficulty + (2.0 - grade) * 0.5))`

### B. El Castigo de Tiempo Subrepticio
La curva original de SuperMemo asume honestidad 100% de los estudiantes; Nexus asume trampa cognitiva. 
Si el reloj `elapsed_seconds` excede **15.0 segundos** desde que leíste la duda hasta que pulsaste continuar, el sistema asume que tuviste que desenterrar violentamente el recuerdo de tu córtex...
Si en la siguiente pantalla, a pesar de esos 15 segundos perdidos intentando rememorar con sudor, descaradamente envías como calificación el **Valor 3 ("Fácil")**... Nexus interceptará esa orden y ejecutará lo siguiente silenciando tu ego:
```python
if grade == 3 and elapsed_seconds > 15.0:
    grade_calc = 2.5 # Te degrada de 'Facil' a un 'Casi Bien' virtual
```
Esto para salvaguardar tu curva. Si pasaste de 15 segundos tartamudeando, la pregunta NO será postergada absurdamente tan lejos; el algoritmo de tiempo forzará a que la veas mucho más temprano en tu vida futura.

### C. La Estabilidad Multiforme (Stability)
Este tensor nos dice la **cantidad literal de días puros** que el conocimiento es estable antes de pudrirse en el olvido.
1. Se inicializan bases de días conservadoras si es la **Primera Vez**:
   - `grade 1` (Difícil) = 1.0 día para volver a ver
   - `grade 2` (Bien) = 3.0 días 
   - `grade 3` (Fácil) = 5.0 días frescos
2. Si es una **Segunda o N-aba Revisión** (ya conocías la Flashcard), entran en juego multiplicadores exponenciales que aceleran abismalmente la estabilidad hacia meses futuros:
   - `grade 1` (Difícil): Se destruye al `0.5` la estabilidad previa (La volverás a ver casi el mismo día).
   - `grade 2` (Bien): La estabilidad salta por `x1.5` de días.
   - `grade 3` (Fácil): Tu anterior Estabilidad pega un salto exponencial de **x2.5** veces la métrica y por tanto la pospone semanas en tu futuro.

### D. El Fallo de Agendamiento
Finalmente inyectamos los Intervalos calculados dentro de la estructura general temporal en el SQLite:
```python
card.last_review = datetime.now(timezone.utc)
card.next_review = card.last_review + timedelta(days=interval_days) # Push en el Futuro
```

---

## 3. Guía de Futuras Reducciones o Mejoras
Si algún día la ciencia avanza significativamente y decides transpirar el SRSEngine clásico anterior hacia el **FSRS** (Scheduler del Olvido Modernista), deberás ubicar la función `calculate_next_review(card, grade, elapsed_seconds)` en el módulo maestro del motor y cambiar esas 20 líneas inyectando un algoritmo de descenso de gradiente para pesos ponderados.
