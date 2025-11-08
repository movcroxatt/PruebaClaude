# Guía de Pruebas Local

## Setup Rápido

### Prerrequisitos
- Python 3.8 o superior
- pip instalado
- Conexión a internet

### Instalación en 4 pasos

```bash
# 1. Clonar y entrar al proyecto
git clone <tu-repo-url>
cd PruebaClaude
git checkout claude/price-scraper-project-011CUucGfZdkakNvG4FnyNHG

# 2. Crear entorno virtual
python3 -m venv venv

# 3. Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate     # Windows

# 4. Instalar dependencias
pip install -r requirements.txt
playwright install chromium
```

## Ejemplos de Uso

### Ejemplo básico
```bash
python scraper.py "https://www.amazon.com/dp/B07RJ18VMF"
```

### Ejemplo con URL completa
```bash
python scraper.py "https://www.amazon.com/CeraVe-Hydrating-Facial-Cleanser-Washing/dp/B07RJ18VMF"
```

### Ver el navegador (modo visible)

Para ver cómo funciona el scraper en tiempo real, edita `scraper.py` línea 31:

**Cambiar:**
```python
headless=True,
```

**Por:**
```python
headless=False,
```

Luego ejecuta normalmente y verás el navegador abriéndose.

## Salida Esperada

```
============================================================
Amazon Product Scraper
============================================================
Loading page: https://www.amazon.com/dp/B07RJ18VMF
Page loaded successfully

============================================================
RESULTS
============================================================

Title: CeraVe Hydrating Facial Cleanser | Moisturizing...

Price: $14.98

Image URL: https://m.media-amazon.com/images/I/...jpg

============================================================
```

## Troubleshooting

### Error: "playwright: command not found"
```bash
# Reinstalar playwright
pip uninstall playwright
pip install playwright==1.48.0
playwright install chromium
```

### Error: "ERR_TUNNEL_CONNECTION_FAILED"
- Verifica tu conexión a internet
- Desactiva VPN si está activa
- Verifica firewall

### Error: "Timeout"
- Amazon puede estar bloqueando
- Espera 2-3 minutos entre intentos
- Prueba con otra URL de producto

### El script no encuentra elementos
- Amazon cambió su estructura HTML
- Intenta con un producto diferente
- Verifica que la URL sea válida

## URLs de Prueba

Aquí hay algunas URLs que puedes usar para probar:

```bash
# Producto 1: CeraVe Cleanser
python scraper.py "https://www.amazon.com/dp/B07RJ18VMF"

# Producto 2: Libro
python scraper.py "https://www.amazon.com/dp/0735211299"

# Producto 3: Electrónica
python scraper.py "https://www.amazon.com/dp/B08N5WRWNW"
```

## Verificar que todo funciona

### Test 1: Verificar Python
```bash
python3 --version
# Debe mostrar: Python 3.8 o superior
```

### Test 2: Verificar entorno virtual activado
```bash
which python
# Debe mostrar la ruta a tu venv
```

### Test 3: Verificar Playwright instalado
```bash
playwright --version
# Debe mostrar: Version 1.48.0
```

### Test 4: Ejecutar script de ayuda
```bash
python scraper.py --help
# Debe mostrar las opciones de uso
```

## Próximos Pasos

Una vez que verifiques que el scraper funciona:

1. Puedes modificar los selectores CSS si Amazon cambia su estructura
2. Agregar más campos (rating, reviews, etc.)
3. Guardar resultados en archivo JSON/CSV
4. Implementar base de datos para histórico de precios

## Notas Importantes

- **Uso responsable**: No hagas demasiadas peticiones seguidas
- **Rate limiting**: Amazon puede bloquear tu IP temporalmente
- **Legal**: Revisa los términos de servicio de Amazon
- **Ética**: Usa el scraper solo para propósitos legítimos

## Contacto

Si tienes problemas, revisa:
1. README.md principal
2. Los comentarios en scraper.py
3. Los mensajes de error que aparecen
