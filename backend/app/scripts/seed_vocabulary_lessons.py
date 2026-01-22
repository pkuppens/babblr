"""Seed script for vocabulary lessons.

Creates Spanish lessons for all CEFR levels (A1-C2) plus basic A1 lessons
for Italian, German, French, and Dutch to ensure the UI is not empty.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database.db import Base
from app.models.models import Lesson, LessonItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample vocabulary lessons data
VOCABULARY_LESSONS = {
    "es": [  # Spanish
        {
            "title": "Saludos y frases básicas",
            "title_en": "Greetings and Basic Phrases",
            "oneliner": "Saluda, despídete y sé amable.",
            "oneliner_en": "Say hello, goodbye, and be polite.",
            "description": "Aprende saludos esenciales y expresiones de cortesía para conversaciones simples.",
            "description_en": "Learn essential greetings and polite expressions for simple conversations.",
            "subject": "Basics",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Hola",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Hello",
                            "pronunciation": "OH-lah",
                            "example": "Hola, ¿cómo estás?",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Buenos días",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Good morning",
                            "pronunciation": "BWEH-nos DEE-ahs",
                            "example": "Buenos días, señor.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Buenas tardes",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Good afternoon",
                            "pronunciation": "BWEH-nas TAR-des",
                            "example": "Buenas tardes, profesora.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Buenas noches",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Good evening/night",
                            "pronunciation": "BWEH-nas NO-ches",
                            "example": "Buenas noches, hasta mañana.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Adiós",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Goodbye",
                            "pronunciation": "ah-DYOHS",
                            "example": "Adiós, nos vemos.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Por favor",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Please",
                            "pronunciation": "por fah-VOR",
                            "example": "Un café, por favor.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "Gracias",
                    "item_metadata": json.dumps(
                        {
                            "translation": "Thank you",
                            "pronunciation": "GRAH-see-ahs",
                            "example": "Gracias por tu ayuda.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "De nada",
                    "item_metadata": json.dumps(
                        {
                            "translation": "You're welcome",
                            "pronunciation": "deh NAH-dah",
                            "example": "—Gracias. —De nada.",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Números del 1 al 20",
            "title_en": "Numbers 1-20",
            "oneliner": "Cuenta y habla de cantidades.",
            "oneliner_en": "Count and talk about quantities.",
            "description": "Aprende a contar del 1 al 20 y usa números en frases simples.",
            "description_en": "Learn to count from 1 to 20 and use numbers in simple sentences.",
            "subject": "Basics",
            "difficulty_level": "A1",
            "order_index": 2,
            "items": [
                {
                    "item_type": "word",
                    "content": "uno",
                    "item_metadata": json.dumps(
                        {
                            "translation": "one",
                            "pronunciation": "OO-no",
                            "example": "Tengo un perro.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "dos",
                    "item_metadata": json.dumps(
                        {
                            "translation": "two",
                            "pronunciation": "dohs",
                            "example": "Tengo dos hermanos.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "tres",
                    "item_metadata": json.dumps(
                        {
                            "translation": "three",
                            "pronunciation": "trehs",
                            "example": "Necesito tres boletos.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "cuatro",
                    "item_metadata": json.dumps(
                        {
                            "translation": "four",
                            "pronunciation": "KWAH-troh",
                            "example": "Hay cuatro sillas.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "cinco",
                    "item_metadata": json.dumps(
                        {
                            "translation": "five",
                            "pronunciation": "SEEN-koh",
                            "example": "Son las cinco.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "seis",
                    "item_metadata": json.dumps(
                        {
                            "translation": "six",
                            "pronunciation": "says",
                            "example": "Trabajo seis días.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "siete",
                    "item_metadata": json.dumps(
                        {
                            "translation": "seven",
                            "pronunciation": "SYEH-teh",
                            "example": "Mi clase empieza a las siete.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "ocho",
                    "item_metadata": json.dumps(
                        {
                            "translation": "eight",
                            "pronunciation": "OH-choh",
                            "example": "Tengo ocho mensajes.",
                        }
                    ),
                    "order_index": 8,
                },
                {
                    "item_type": "word",
                    "content": "nueve",
                    "item_metadata": json.dumps(
                        {
                            "translation": "nine",
                            "pronunciation": "NWEH-veh",
                            "example": "El tren sale a las nueve.",
                        }
                    ),
                    "order_index": 9,
                },
                {
                    "item_type": "word",
                    "content": "diez",
                    "item_metadata": json.dumps(
                        {
                            "translation": "ten",
                            "pronunciation": "dyehs",
                            "example": "Hay diez estudiantes.",
                        }
                    ),
                    "order_index": 10,
                },
            ],
        },
        {
            "title": "Rutinas diarias",
            "title_en": "Daily Routines",
            "oneliner": "Habla de tu día y tus hábitos.",
            "oneliner_en": "Talk about your day and habits.",
            "description": "Practica verbos comunes y frases de tiempo para actividades diarias.",
            "description_en": "Practice common verbs and time phrases for daily activities.",
            "subject": "Daily Life",
            "difficulty_level": "A2",
            "order_index": 3,
            "items": [
                {
                    "item_type": "word",
                    "content": "levantarse",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to get up",
                            "pronunciation": "leh-van-TAHR-seh",
                            "example": "Me levanto a las siete.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "desayunar",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to have breakfast",
                            "pronunciation": "deh-sah-yoo-NAR",
                            "example": "Desayuno café y pan.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "almuerzo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "lunch",
                            "pronunciation": "al-MWER-so",
                            "example": "El almuerzo es a la una.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "cenar",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to have dinner",
                            "pronunciation": "seh-NAR",
                            "example": "Cenamos en casa.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "a menudo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "often",
                            "pronunciation": "ah meh-NOO-doh",
                            "example": "A menudo voy al gimnasio.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "siempre",
                    "item_metadata": json.dumps(
                        {
                            "translation": "always",
                            "pronunciation": "SYEM-preh",
                            "example": "Siempre estudio por la noche.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "nunca",
                    "item_metadata": json.dumps(
                        {
                            "translation": "never",
                            "pronunciation": "NOON-kah",
                            "example": "Nunca llego tarde.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "después",
                    "item_metadata": json.dumps(
                        {
                            "translation": "after, later",
                            "pronunciation": "dehs-PWEHS",
                            "example": "Después del trabajo, camino al parque.",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Compras y precios",
            "title_en": "Shopping and Prices",
            "oneliner": "Compra ropa, pide tallas y paga.",
            "oneliner_en": "Buy clothes, ask sizes, and pay.",
            "description": "Usa vocabulario de compras para preguntar precios, tallas y pagos.",
            "description_en": "Use common shopping words to ask about prices, sizes, and payment.",
            "subject": "Everyday Tasks",
            "difficulty_level": "A2",
            "order_index": 4,
            "items": [
                {
                    "item_type": "word",
                    "content": "barato",
                    "item_metadata": json.dumps(
                        {
                            "translation": "cheap",
                            "pronunciation": "bah-RAH-toh",
                            "example": "Esta camiseta es barata.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "caro",
                    "item_metadata": json.dumps(
                        {
                            "translation": "expensive",
                            "pronunciation": "KAH-roh",
                            "example": "El abrigo es caro.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "rebaja",
                    "item_metadata": json.dumps(
                        {
                            "translation": "sale, discount",
                            "pronunciation": "reh-BAH-hah",
                            "example": "Hay rebajas este fin de semana.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "talla",
                    "item_metadata": json.dumps(
                        {
                            "translation": "size",
                            "pronunciation": "TAH-yah",
                            "example": "¿Tiene esta camisa en talla M?",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "probarse",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to try on",
                            "pronunciation": "proh-BAR-seh",
                            "example": "Quiero probarme los zapatos.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "cuenta",
                    "item_metadata": json.dumps(
                        {
                            "translation": "bill",
                            "pronunciation": "KWEN-tah",
                            "example": "La cuenta, por favor.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "efectivo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "cash",
                            "pronunciation": "eh-fehk-TEE-voh",
                            "example": "Pago en efectivo.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "tarjeta",
                    "item_metadata": json.dumps(
                        {
                            "translation": "card",
                            "pronunciation": "tar-HEH-tah",
                            "example": "¿Puedo pagar con tarjeta?",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Viajes y direcciones",
            "title_en": "Travel and Directions",
            "oneliner": "Pide ayuda, billetes y direcciones.",
            "oneliner_en": "Ask for help, tickets, and directions.",
            "description": "Gana confianza con vocabulario de viaje para estaciones, billetes y rutas.",
            "description_en": "Build confidence with travel vocabulary for stations, tickets, and routes.",
            "subject": "Travel",
            "difficulty_level": "B1",
            "order_index": 5,
            "items": [
                {
                    "item_type": "word",
                    "content": "billete de ida y vuelta",
                    "item_metadata": json.dumps(
                        {
                            "translation": "round-trip ticket",
                            "pronunciation": "bee-YEH-teh deh EE-dah ee VWEL-tah",
                            "example": "Quiero un billete de ida y vuelta a Valencia.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "horario",
                    "item_metadata": json.dumps(
                        {
                            "translation": "schedule",
                            "pronunciation": "oh-RAH-ree-oh",
                            "example": "¿Dónde puedo ver el horario de trenes?",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "andén",
                    "item_metadata": json.dumps(
                        {
                            "translation": "platform",
                            "pronunciation": "ahn-DEN",
                            "example": "El tren sale del andén tres.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "equipaje de mano",
                    "item_metadata": json.dumps(
                        {
                            "translation": "carry-on luggage",
                            "pronunciation": "eh-kee-PAH-heh deh MAH-noh",
                            "example": "Solo llevo equipaje de mano.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "hacer una reserva",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to make a reservation",
                            "pronunciation": "ah-SEHR OO-nah reh-SEHR-vah",
                            "example": "Necesito hacer una reserva para mañana.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "perderse",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to get lost",
                            "pronunciation": "pehr-DEHR-seh",
                            "example": "Me perdí en el centro histórico.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "doblar a la izquierda",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to turn left",
                            "pronunciation": "doh-BLAR ah lah ees-KYEHR-dah",
                            "example": "Doble a la izquierda en la esquina.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "seguir recto",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to go straight",
                            "pronunciation": "seh-GEER REHK-toh",
                            "example": "Siga recto hasta la plaza.",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Trabajo y estudios",
            "title_en": "Work and Study",
            "oneliner": "Habla de proyectos, metas y plazos.",
            "oneliner_en": "Talk about projects, goals, and deadlines.",
            "description": "Usa vocabulario de trabajo y estudio para planificar y colaborar.",
            "description_en": "Use workplace and study vocabulary for planning and collaboration.",
            "subject": "Work and Study",
            "difficulty_level": "B2",
            "order_index": 6,
            "items": [
                {
                    "item_type": "word",
                    "content": "currículum",
                    "item_metadata": json.dumps(
                        {
                            "translation": "resume",
                            "pronunciation": "koo-REE-koo-loom",
                            "example": "Actualicé mi currículum ayer.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "entrevista de trabajo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "job interview",
                            "pronunciation": "en-treh-VEE-stah deh trah-BAH-ho",
                            "example": "Tengo una entrevista de trabajo el lunes.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "plazo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "deadline",
                            "pronunciation": "PLAH-soh",
                            "example": "El plazo de entrega es mañana.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "responsabilidad",
                    "item_metadata": json.dumps(
                        {
                            "translation": "responsibility",
                            "pronunciation": "rehs-pon-sah-bee-lee-DAHD",
                            "example": "Es una gran responsabilidad.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "equipo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "team",
                            "pronunciation": "eh-KEE-poh",
                            "example": "Mi equipo trabaja en remoto.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "destacar",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to stand out",
                            "pronunciation": "dehs-tah-KAR",
                            "example": "Quiero destacar en la presentación.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "aprender de los errores",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to learn from mistakes",
                            "pronunciation": "ah-pren-DEHR deh lohs eh-RRO-res",
                            "example": "Es importante aprender de los errores.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "objetivo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "goal",
                            "pronunciation": "oh-heh-TEE-voh",
                            "example": "Nuestro objetivo es mejorar el servicio.",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Noticias y sociedad",
            "title_en": "News and Society",
            "oneliner": "Habla de temas sociales y noticias.",
            "oneliner_en": "Discuss social issues and current events.",
            "description": "Desarrolla vocabulario para noticias y debates públicos.",
            "description_en": "Develop vocabulary for news reports and public discussions.",
            "subject": "Current Affairs",
            "difficulty_level": "C1",
            "order_index": 7,
            "items": [
                {
                    "item_type": "word",
                    "content": "desigualdad",
                    "item_metadata": json.dumps(
                        {
                            "translation": "inequality",
                            "pronunciation": "dehs-ee-goo-ahl-DAHD",
                            "example": "La desigualdad social es un tema complejo.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "sostenibilidad",
                    "item_metadata": json.dumps(
                        {
                            "translation": "sustainability",
                            "pronunciation": "sos-teh-nee-bee-lee-DAHD",
                            "example": "La sostenibilidad es clave en las ciudades modernas.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "movilización",
                    "item_metadata": json.dumps(
                        {
                            "translation": "mobilization",
                            "pronunciation": "moh-vee-lee-sah-THYON",
                            "example": "La movilización ciudadana fue masiva.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "polarización",
                    "item_metadata": json.dumps(
                        {
                            "translation": "polarization",
                            "pronunciation": "poh-lah-ree-sah-THYON",
                            "example": "La polarización política ha aumentado.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "debate público",
                    "item_metadata": json.dumps(
                        {
                            "translation": "public debate",
                            "pronunciation": "deh-BAH-teh POO-blee-koh",
                            "example": "El debate público fue intenso.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "medios de comunicación",
                    "item_metadata": json.dumps(
                        {
                            "translation": "media",
                            "pronunciation": "MEH-dee-ohs deh koh-moo-nee-kah-SYON",
                            "example": "Los medios de comunicación influyen en la opinión.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "cifra",
                    "item_metadata": json.dumps(
                        {
                            "translation": "figure, statistic",
                            "pronunciation": "SEE-frah",
                            "example": "La cifra de desempleo bajó.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "tendencia",
                    "item_metadata": json.dumps(
                        {
                            "translation": "trend",
                            "pronunciation": "ten-DEN-syah",
                            "example": "La tendencia muestra un cambio positivo.",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
        {
            "title": "Modismos y matices",
            "title_en": "Idioms and Nuance",
            "oneliner": "Entiende modismos y matices.",
            "oneliner_en": "Understand idioms and subtle meanings.",
            "description": "Aprende modismos y expresiones comunes de hablantes nativos.",
            "description_en": "Learn common idioms and expressions used by native speakers.",
            "subject": "Idioms",
            "difficulty_level": "C2",
            "order_index": 8,
            "items": [
                {
                    "item_type": "word",
                    "content": "estar en las nubes",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to have one's head in the clouds",
                            "pronunciation": "es-TAR en las NOO-bes",
                            "example": "Estás en las nubes; no escuchas.",
                        }
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "costar un ojo de la cara",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to cost an arm and a leg",
                            "pronunciation": "kos-TAR oon OH-ho deh lah KAH-rah",
                            "example": "Ese reloj cuesta un ojo de la cara.",
                        }
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "ponerse las pilas",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to get one's act together",
                            "pronunciation": "poh-NER-seh las PEE-las",
                            "example": "Tenemos que ponernos las pilas.",
                        }
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "dar en el clavo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to hit the nail on the head",
                            "pronunciation": "DAR en el KLAH-voh",
                            "example": "Con tu comentario diste en el clavo.",
                        }
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "no tener pelos en la lengua",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to be very direct",
                            "pronunciation": "noh teh-NER PEH-los en lah LEN-gwah",
                            "example": "Ella no tiene pelos en la lengua.",
                        }
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "estar hecho polvo",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to be exhausted",
                            "pronunciation": "es-TAR EH-choh POL-voh",
                            "example": "Después del viaje, estaba hecho polvo.",
                        }
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "meter la pata",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to put one's foot in it",
                            "pronunciation": "meh-TER lah PAH-tah",
                            "example": "Metí la pata en la reunión.",
                        }
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "tirar la casa por la ventana",
                    "item_metadata": json.dumps(
                        {
                            "translation": "to spare no expense",
                            "pronunciation": "tee-RAR lah KAH-sah por lah ven-TAH-nah",
                            "example": "En su boda tiraron la casa por la ventana.",
                        }
                    ),
                    "order_index": 8,
                },
            ],
        },
    ],
    "it": [  # Italian
        {
            "title": "Saluti e frasi di base",
            "title_en": "Greetings and Basic Phrases",
            "oneliner": "Saluta, congedati e sii cortese.",
            "oneliner_en": "Say hello, goodbye, and be polite.",
            "description": "Impara saluti essenziali ed espressioni di cortesia per conversazioni semplici.",
            "description_en": "Learn essential greetings and polite expressions in Italian",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Ciao",
                    "item_metadata": json.dumps(
                        {"translation": "Hello/Goodbye", "pronunciation": "CHOW"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Buongiorno",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "bwon-JOR-no"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Buonasera",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "bwoh-nah-SEH-rah"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Per favore",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "per fah-VOH-reh"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Grazie",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "GRAH-tsee-eh"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Prego",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "PREH-goh"}
                    ),
                    "order_index": 6,
                },
            ],
        },
    ],
    "de": [  # German
        {
            "title": "Begrüßungen und Grundausdrücke",
            "title_en": "Greetings and Basic Phrases",
            "oneliner": "Grüßen, verabschieden und höflich sein.",
            "oneliner_en": "Say hello, goodbye, and be polite.",
            "description": "Lerne wichtige Grüße und höfliche Ausdrücke für einfache Gespräche.",
            "description_en": "Learn essential greetings and polite expressions in German",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Hallo",
                    "item_metadata": json.dumps(
                        {"translation": "Hello", "pronunciation": "HAH-loh"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Guten Morgen",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "GOO-ten MOR-gen"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Guten Tag",
                    "item_metadata": json.dumps(
                        {"translation": "Good day", "pronunciation": "GOO-ten TAHK"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Guten Abend",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "GOO-ten AH-bent"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Auf Wiedersehen",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "owf VEE-der-zay-en"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Bitte",
                    "item_metadata": json.dumps(
                        {"translation": "Please/You're welcome", "pronunciation": "BIT-teh"}
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "Danke",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "DAHN-keh"}
                    ),
                    "order_index": 7,
                },
            ],
        },
    ],
    "fr": [  # French
        {
            "title": "Salutations et expressions de base",
            "title_en": "Greetings and Basic Phrases",
            "oneliner": "Salue, dis au revoir et sois poli.",
            "oneliner_en": "Say hello, goodbye, and be polite.",
            "description": "Apprends des salutations essentielles et des formules de politesse pour des conversations simples.",
            "description_en": "Learn essential greetings and polite expressions in French",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Bonjour",
                    "item_metadata": json.dumps(
                        {"translation": "Hello/Good morning", "pronunciation": "bon-ZHOOR"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Bonsoir",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "bon-SWAHR"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Au revoir",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "oh ruh-VWAHR"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "S'il vous plaît",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "seel voo PLAY"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Merci",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "mehr-SEE"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "De rien",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "duh RYEHN"}
                    ),
                    "order_index": 6,
                },
            ],
        },
    ],
    "nl": [  # Dutch
        {
            "title": "Begroetingen en basiszinnen",
            "title_en": "Greetings and Basic Phrases",
            "oneliner": "Groet, neem afscheid en wees beleefd.",
            "oneliner_en": "Say hello, goodbye, and be polite.",
            "description": "Leer basisgroeten en beleefde uitdrukkingen voor eenvoudige gesprekken.",
            "description_en": "Learn essential greetings and polite expressions in Dutch",
            "difficulty_level": "A1",
            "order_index": 1,
            "items": [
                {
                    "item_type": "word",
                    "content": "Hallo",
                    "item_metadata": json.dumps(
                        {"translation": "Hello", "pronunciation": "HAH-loh"}
                    ),
                    "order_index": 1,
                },
                {
                    "item_type": "word",
                    "content": "Goedemorgen",
                    "item_metadata": json.dumps(
                        {"translation": "Good morning", "pronunciation": "KHOOH-deh-MOR-ghen"}
                    ),
                    "order_index": 2,
                },
                {
                    "item_type": "word",
                    "content": "Goedemiddag",
                    "item_metadata": json.dumps(
                        {"translation": "Good afternoon", "pronunciation": "KHOOH-deh-MID-dahkh"}
                    ),
                    "order_index": 3,
                },
                {
                    "item_type": "word",
                    "content": "Goedenavond",
                    "item_metadata": json.dumps(
                        {"translation": "Good evening", "pronunciation": "KHOOH-den-AH-vont"}
                    ),
                    "order_index": 4,
                },
                {
                    "item_type": "word",
                    "content": "Tot ziens",
                    "item_metadata": json.dumps(
                        {"translation": "Goodbye", "pronunciation": "tot ZEENS"}
                    ),
                    "order_index": 5,
                },
                {
                    "item_type": "word",
                    "content": "Alsjeblieft",
                    "item_metadata": json.dumps(
                        {"translation": "Please", "pronunciation": "AHL-shuh-bleeft"}
                    ),
                    "order_index": 6,
                },
                {
                    "item_type": "word",
                    "content": "Dank je",
                    "item_metadata": json.dumps(
                        {"translation": "Thank you", "pronunciation": "dahnk yuh"}
                    ),
                    "order_index": 7,
                },
                {
                    "item_type": "word",
                    "content": "Graag gedaan",
                    "item_metadata": json.dumps(
                        {"translation": "You're welcome", "pronunciation": "khrahkh kheh-DAHN"}
                    ),
                    "order_index": 8,
                },
            ],
        },
    ],
}


async def seed_vocabulary_lessons():
    """Seed vocabulary lessons into the database."""
    # Create async engine
    engine = create_async_engine(settings.babblr_conversation_database_url, echo=False)

    # Create async session factory
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Import models to ensure they're registered
            from app.models import models  # noqa: F401

            # Create tables if they don't exist
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Starting vocabulary lessons seed...")

            lessons_created = 0
            items_created = 0

            for language, lessons in VOCABULARY_LESSONS.items():
                logger.info(f"Seeding vocabulary lessons for language: {language}")

                for lesson_data in lessons:
                    # Check if lesson already exists (by title and language)
                    from sqlalchemy import select

                    title_en = lesson_data.get("title_en")
                    match_conditions = [Lesson.title == lesson_data["title"]]
                    if title_en:
                        match_conditions.extend(
                            [Lesson.title == title_en, Lesson.title_en == title_en]
                        )

                    existing = await session.execute(
                        select(Lesson).where(
                            Lesson.language == language,
                            Lesson.lesson_type == "vocabulary",
                            or_(*match_conditions),
                        )
                    )
                    existing_lesson = existing.scalars().first()
                    if existing_lesson:
                        updated = False
                        update_map = {
                            "title": lesson_data.get("title"),
                            "title_en": lesson_data.get("title_en"),
                            "oneliner": lesson_data.get("oneliner"),
                            "oneliner_en": lesson_data.get("oneliner_en"),
                            "description": lesson_data.get("description"),
                            "description_en": lesson_data.get("description_en"),
                            "subject": lesson_data.get("subject"),
                            "difficulty_level": lesson_data.get("difficulty_level"),
                            "order_index": lesson_data.get("order_index"),
                        }

                        for field_name, new_value in update_map.items():
                            if (
                                new_value is not None
                                and getattr(existing_lesson, field_name) != new_value
                            ):
                                setattr(existing_lesson, field_name, new_value)
                                updated = True

                        if updated:
                            existing_lesson.updated_at = datetime.now(timezone.utc)
                            logger.info(f"Updated lesson '{lesson_data['title']}' for {language}.")
                        else:
                            logger.info(
                                f"Lesson '{lesson_data['title']}' already exists for {language}, skipping..."
                            )
                        continue

                    # Create lesson
                    lesson = Lesson(
                        language=language,
                        lesson_type="vocabulary",
                        title=lesson_data["title"],
                        title_en=lesson_data.get("title_en"),
                        oneliner=lesson_data.get("oneliner"),
                        oneliner_en=lesson_data.get("oneliner_en"),
                        description=lesson_data["description"],
                        description_en=lesson_data.get("description_en"),
                        subject=lesson_data.get("subject"),
                        difficulty_level=lesson_data["difficulty_level"],
                        order_index=lesson_data["order_index"],
                        is_active=True,
                        created_at=datetime.now(timezone.utc),
                    )

                    session.add(lesson)
                    await session.flush()  # Get lesson.id

                    # Create lesson items
                    for item_data in lesson_data["items"]:
                        item = LessonItem(
                            lesson_id=lesson.id,
                            item_type=item_data["item_type"],
                            content=item_data["content"],
                            item_metadata=item_data["item_metadata"],
                            order_index=item_data["order_index"],
                            created_at=datetime.now(timezone.utc),
                        )
                        session.add(item)
                        items_created += 1

                    lessons_created += 1
                    logger.info(f"Created lesson: {lesson_data['title']} ({language})")

            await session.commit()

            logger.info(f"Seed completed: {lessons_created} lessons, {items_created} items created")

        except Exception as e:
            logger.error(f"Error seeding vocabulary lessons: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_vocabulary_lessons())
