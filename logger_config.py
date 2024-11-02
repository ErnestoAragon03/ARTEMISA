# logger_config.py
import logging

# Configura el logger
logging.basicConfig(
    filename='Artemisa_log.txt', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Crea un logger que puede ser usado por otros módulos
logger = logging.getLogger('Artemisa')
